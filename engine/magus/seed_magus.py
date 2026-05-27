"""
Seed the MAGUS SQLite database from world/magus/classes.json.

Run:
    python -m engine.magus.seed_magus

Idempotent — safe to run multiple times. Uses upsert so existing IDs
are preserved (important for FK consistency across re-seeds).
"""

from __future__ import annotations

import json
import re
import sqlite3
from itertools import product as iproduct
from pathlib import Path
from typing import Any

from engine.magus.db import DB_PATH, get_connection, init_db

ROOT         = Path(__file__).parent.parent.parent
CLASSES_FILE = ROOT / "world" / "magus" / "classes.json"


# ---------------------------------------------------------------------------
# Dice formula parser
# ---------------------------------------------------------------------------

def _avg_advantage(dice_count: int, dice_sides: int) -> float:
    """E[max(X, Y)] where X and Y are independent sums of dice_count × d<dice_sides>."""
    all_sums = [sum(roll) for roll in iproduct(range(1, dice_sides + 1), repeat=dice_count)]
    n = len(all_sums)
    total = sum(max(a, b) for a in all_sums for b in all_sums)
    return total / (n * n)


def parse_formula(raw: str) -> dict[str, Any]:
    """Parse a MAGUS dice formula string into DB-ready components.

    Supported forms: k6+12, 2k6+6, k10+8, 3k6, 3k6(2x)
    """
    s = raw.strip().lower()
    advantage = "(2x)" in s
    s = s.replace("(2x)", "").strip()

    m = re.match(r'^(\d*)k(\d+)([+-]\d+)?$', s)
    if not m:
        raise ValueError(f"Unrecognised dice formula: {raw!r}")

    dice_count = int(m.group(1)) if m.group(1) else 1
    dice_sides = int(m.group(2))
    modifier   = int(m.group(3)) if m.group(3) else 0

    min_val = dice_count + modifier
    max_val = dice_count * dice_sides + modifier

    if advantage:
        base_avg = _avg_advantage(dice_count, dice_sides)
    else:
        base_avg = dice_count * (dice_sides + 1) / 2.0

    return {
        "formula":    raw,
        "dice_count": dice_count,
        "dice_sides": dice_sides,
        "modifier":   modifier,
        "advantage":  1 if advantage else 0,
        "avg":        round(base_avg + modifier, 2),
        "min_val":    min_val,
        "max_val":    max_val,
    }


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------

def _upsert_formula(conn: sqlite3.Connection, raw: str) -> int:
    """Insert formula if missing; return its id either way."""
    f = parse_formula(raw)
    conn.execute(
        """
        INSERT INTO dice_formulas
            (formula, dice_count, dice_sides, modifier, advantage, avg, min_val, max_val)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(formula) DO NOTHING
        """,
        (f["formula"], f["dice_count"], f["dice_sides"], f["modifier"],
         f["advantage"], f["avg"], f["min_val"], f["max_val"]),
    )
    return conn.execute(
        "SELECT id FROM dice_formulas WHERE formula = ?", (raw,)
    ).fetchone()["id"]


def _fp_formula_from_max(max_val: int) -> str:
    """Derive the FP-per-level formula from its maximum value.

    In MAGUS the FP roll is always k6+X where X = max_val - 6.
    e.g. 11 -> k6+5, 10 -> k6+4, 6 -> k6
    """
    modifier = max_val - 6
    return "k6" if modifier == 0 else f"k6+{modifier}"


def _upsert_class(conn: sqlite3.Connection, cls: dict) -> int:
    """Upsert one class row; return its id."""
    nev = cls["nev"]
    hv  = cls.get("harcertekek", {})
    ep  = cls.get("ep", {})
    kp  = cls.get("kp", {})

    # ep.szintenként stores the FP-per-level formula maximum, not a flat EP value
    fp_per_szint_formula_id = None
    fp_max = ep.get("szintenként")
    if fp_max:
        fp_per_szint_formula_id = _upsert_formula(conn, _fp_formula_from_max(fp_max))

    conn.execute(
        """
        INSERT INTO kasztok
            (nev, alap_ke, alap_te, alap_ve, alap_ce,
             alap_ep, fp_per_szint_formula_id,
             alap_kp, kp_per_szint,
             hm_per_szint, kotelezo_hm_te, kotelezo_hm_ve)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(nev) DO UPDATE SET
            alap_ke                 = excluded.alap_ke,
            alap_te                 = excluded.alap_te,
            alap_ve                 = excluded.alap_ve,
            alap_ce                 = excluded.alap_ce,
            alap_ep                 = excluded.alap_ep,
            fp_per_szint_formula_id = excluded.fp_per_szint_formula_id,
            alap_kp                 = excluded.alap_kp,
            kp_per_szint            = excluded.kp_per_szint,
            hm_per_szint            = excluded.hm_per_szint,
            kotelezo_hm_te          = excluded.kotelezo_hm_te,
            kotelezo_hm_ve          = excluded.kotelezo_hm_ve
        """,
        (
            nev,
            hv.get("ke", 0), hv.get("te", 0), hv.get("ve", 0), hv.get("ce", 0),
            ep.get("alap", 0), fp_per_szint_formula_id,
            kp.get("alap", 0), kp.get("szintenként", 0),
            hv.get("hm", 0), hv.get("hm_min_te", 0), hv.get("hm_min_ve", 0),
        ),
    )
    return conn.execute(
        "SELECT id FROM kasztok WHERE nev = ?", (nev,)
    ).fetchone()["id"]


def _seed_class(conn: sqlite3.Connection, cls: dict) -> None:
    kaszt_id = _upsert_class(conn, cls)

    # Property rolling formulas (class overrides only)
    for prop, raw_formula in cls.get("tulajdonsag_dobas", {}).items():
        formula_id = _upsert_formula(conn, raw_formula)
        conn.execute(
            """
            INSERT INTO kaszt_tulajdonsag_dobas (kaszt_id, tulajdonsag, formula_id)
            VALUES (?, ?, ?)
            ON CONFLICT(kaszt_id, tulajdonsag) DO UPDATE SET formula_id = excluded.formula_id
            """,
            (kaszt_id, prop, formula_id),
        )

    # XP thresholds  ("13+" → szint 13)
    for szint_str, xp_min in cls.get("xp_kuszob", {}).items():
        szint = int(szint_str.replace("+", ""))
        conn.execute(
            """
            INSERT INTO kaszt_xp_kuszob (kaszt_id, szint, xp_min)
            VALUES (?, ?, ?)
            ON CONFLICT(kaszt_id, szint) DO UPDATE SET xp_min = excluded.xp_min
            """,
            (kaszt_id, szint, xp_min),
        )


# ---------------------------------------------------------------------------
# Skills (képzettségek)
# (id, nev, kategoria, tipus, ar_alapfok, ar_mesterfok)
# IDs are explicit and stable — do not renumber.
# ---------------------------------------------------------------------------

_SKILLS: list[tuple] = [
    # --- HARCI ---
    ( 1, "Ökölharc",                     "harci",      "alap_mester",  3,    15),
    ( 2, "Birkózás",                      "harci",      "alap_mester",  8,    15),
    ( 3, "Fegyverhasználat",              "harci",      "alap_mester",  3,    30),
    ( 4, "Pajzs használata",              "harci",      "alap_mester",  5,    30),
    ( 5, "Fegyverdobás",                  "harci",      "alap_mester",  4,    40),
    ( 6, "Fegyvertörés",                  "harci",      "alap_mester",  5,    20),
    ( 7, "Lefegyverzés",                  "harci",      "alap_mester",  7,    18),
    ( 8, "Nehézvért viselet",             "harci",      "alap_mester",  3,    27),
    ( 9, "Kétkezes harc",                 "harci",      "alap_mester", 15,    25),
    (10, "Vakharc",                       "harci",      "alap_mester", 10,    30),
    (11, "Fegyverismeret",                "harci",      "alap_mester", 10,    20),
    (12, "Hadvezetés",                    "harci",      "alap_mester",  5,    20),
    # --- TUDOMÁNYOS ---
    (13, "Írás/olvasás",                  "tudomanyos", "alap_mester",  5,    25),
    (14, "Nyelvtudás",                    "tudomanyos", "alap_mester",  1,    20),
    (15, "Ősi nyelv ismerete",            "tudomanyos", "alap_mester", 10,    60),
    (16, "Időjóslás",                     "tudomanyos", "alap_mester",  3,    15),
    (17, "Térképészet",                   "tudomanyos", "alap_mester", 10,    17),
    (18, "Heraldika",                     "tudomanyos", "alap_mester",  5,    15),
    (19, "Legendaismeret",                "tudomanyos", "alap_mester", 10,    50),
    (20, "Történelemismeret",             "tudomanyos", "alap_mester",  5,    20),
    (21, "Vallásismeret",                 "tudomanyos", "alap_mester",  5,    25),
    (22, "Építészet",                     "tudomanyos", "alap_mester",  5,    20),
    (23, "Méregkeverés/semlegesítés",     "tudomanyos", "alap_mester", 15,    60),
    (24, "Herbalizmus",                   "tudomanyos", "alap_mester",  5,    35),
    (25, "Sebgyógyítás",                  "tudomanyos", "alap_mester", 15,    30),
    (26, "Pszi",                          "tudomanyos", "alap_mester", 10,    55),
    (27, "Alkímia",                       "tudomanyos", "alap_mester", 10,    40),
    (28, "Élettan",                       "tudomanyos", "alap_mester", 15,    45),
    (29, "Mágia használat",               "tudomanyos", "alap_mester", 15,    45),
    (30, "Demonológia",                   "tudomanyos", "alap_mester", 20,    55),
    (31, "Rúnamágia",                     "tudomanyos", "alap_mester", 18,    45),
    (32, "Drágakőmágia",                  "tudomanyos", "alap_mester", None,  52),
    # --- VILÁGI ---
    (33, "Idomítás",                      "vilagi",     "alap_mester",  8,    20),
    (34, "Nyomolvasás/eltűntetés",        "vilagi",     "alap_mester", 10,    45),
    (35, "Erdőjárás",                     "vilagi",     "alap_mester",  5,    14),
    (36, "Vadászat/halászat",             "vilagi",     "alap_mester",  8,    15),
    (37, "Lovaglás",                      "vilagi",     "alap_mester",  1,    15),
    (38, "Kocsihajtás",                   "vilagi",     "alap_mester",  2,    15),
    (39, "Szexuális kultúra",             "vilagi",     "alap_mester",  5,    30),
    (40, "Hajózás",                       "vilagi",     "alap_mester", 15,    40),
    (41, "Éneklés/zenélés",               "vilagi",     "alap_mester",  5,    30),
    (42, "Tánc",                          "vilagi",     "alap_mester",  3,    30),
    (43, "Hangutánzás",                   "vilagi",     "alap_mester",  3,    16),
    (44, "Értékbecslés",                  "vilagi",     "alap_mester",  5,    11),
    (45, "Csapdaállítás",                 "vilagi",     "alap_mester", 10,    20),
    (46, "Csomózás",                      "vilagi",     "alap_mester",  7,    24),
    (47, "Zsonglőrködés",                 "vilagi",     "alap_mester",  3,    10),
    (48, "Futás",                         "vilagi",     "alap_mester",  9,    24),
    (49, "Szakma",                        "vilagi",     "alap_mester",  2,    15),
    (50, "Mászás",                        "vilagi",     "szazalekos",  None, None),
    (51, "Esés",                          "vilagi",     "szazalekos",  None, None),
    (52, "Ugrás",                         "vilagi",     "szazalekos",  None, None),
    # --- ALVILÁGI ---
    (53, "Kocsmai verekedés",             "alvilagi",   "alap_mester",  3,    15),
    (54, "Hátbaszúrás",                   "alvilagi",   "alap_mester", 10,    25),
    (55, "Hamiskártya",                   "alvilagi",   "alap_mester", 10,    20),
    (56, "Kötélből szabadulás",           "alvilagi",   "alap_mester",  8,    16),
    (57, "Álcázás/álruha",                "alvilagi",   "alap_mester", 12,    24),
    (58, "Lopózás",                       "alvilagi",   "szazalekos",  None, None),
    (59, "Rejtőzködés",                   "alvilagi",   "szazalekos",  None, None),
    (60, "Kötéltánc",                     "alvilagi",   "szazalekos",  None, None),
    (61, "Zsebmetszés",                   "alvilagi",   "szazalekos",  None, None),
    (62, "Csapdafelfedezés",              "alvilagi",   "szazalekos",  None, None),
    (63, "Zárnyitás",                     "alvilagi",   "szazalekos",  None, None),
    (64, "Titkosajtó keresés",            "alvilagi",   "szazalekos",  None, None),
    # --- VILÁGI (folytatás, 65-66) ---
    (65, "Etikett",                       "vilagi",     "alap_mester",  8,    15),
    (66, "Úszás",                         "vilagi",     "alap_mester",  2,    10),
    # --- HARCI (folytatás) ---
    (67, "Harci láz",                     "harci",      "alap_mester",  8,    15),
    (68, "Hadrend",                       "harci",      "alap_mester",  3,    20),
    (69, "Harc helyhez kötve",            "harci",      "alap_mester",  4,    12),
    # Mesterfokú fegyverhasználathoz tanulható harci képzettségek
    (70, "Kínokozás",                     "harci",      "alap_mester",  9,    20),
    (71, "Pusztítás",                     "harci",      "alap_mester", 15,    30),
    (72, "Kiegészítő támadás 1",          "harci",      "alap_mester",  0,     8),
    (73, "Kiegészítő támadás 2",          "harci",      "alap_mester",  7,    15),
    (74, "Különleges fegyver hasz.",      "harci",      "alap_mester", 15,    30),
    (75, "Lovas íjászat",                 "harci",      "alap_mester", 15,    30),
    (76, "Célzás",                        "harci",      "alap_mester", 20,    35),
    # --- VILÁGI (folytatás) ---
    (77, "Állatismeret",                  "vilagi",     "alap_mester",  1,     6),
    # --- HARCI (folytatás) ---
    (78, "Hárítófegyver használat",       "harci",      "alap_mester",  8,    15),
    (79, "Földharc",                      "harci",      "alap_mester",  5,    12),
    (80, "Belharc",                       "harci",      "alap_mester",  3,    10),
    (81, "Közös harcmodor",               "harci",      "alap_mester",  7,    30),
    (82, "Ikerharc",                      "harci",      "alap_mester", 12,    45),
    # --- TUDOMÁNYOS (folytatás) ---
    (83, "Emberismeret",                  "tudomanyos", "alap_mester",  7,    22),
    (84, "Mágia ismeret",                 "tudomanyos", "alap_mester",  5,    25),
    (85, "Mechanika",                     "tudomanyos", "alap_mester",  8,    25),
    # --- VILÁGI (folytatás) ---
    (86, "Szájról olvasás",               "vilagi",     "alap_mester",  7,    10),
    (87, "Mellébeszélés",                 "vilagi",     "alap_mester",  3,     9),
    (88, "Kínzás",                        "vilagi",     "alap_mester",  2,    15),
    (89, "Kínzás elviselése",             "vilagi",     "alap_mester",  5,    12),
    (90, "Helyismeret",                   "vilagi",     "alap_mester",  1,     8),
    (91, "Festészet/rajzolás",            "vilagi",     "alap_mester",  3,    18),
    (92, "Éberség/Észlelés",              "vilagi",     "szazalekos",  None, None),
    (93, "Követés/Lerázás",               "alvilagi",   "szazalekos",  None, None),
    (94, "Hamisítás",                     "alvilagi",   "alap_mester", 11,    24),
]


_CODES: list[tuple] = [
    # NJK type minimum total property thresholds
    ("njk_tipus_min_pont", "atlagos", 130, "Átlagos NJK — minimum tulajdonság összérték"),
    ("njk_tipus_min_pont", "kiemelt", 135, "Kiemelt NJK — minimum tulajdonság összérték"),
    ("njk_tipus_min_pont", "elit",    140, "Elit NJK — minimum tulajdonság összérték"),
    # HM distribution strategies
    ("hm_elosztasi_mod", "1", 1, "TÉ+VÉ egyensúly: VÉ-TÉ=45 tartva; ha pontosan 45, TÉ-re megy"),
    ("hm_elosztasi_mod", "2", 2, "Mind CÉ-re"),
    ("hm_elosztasi_mod", "3", 3, "Mind VÉ-re"),
    ("hm_elosztasi_mod", "4", 4, "Mind TÉ-re"),
]


# ---------------------------------------------------------------------------
# Special training (különleges felkészítés) — max cap above formula max_val
# All entries use max_bonus=1 (one above the formula's natural maximum).
# ---------------------------------------------------------------------------

def _kf(classes: list[str], props: list[str], bonus: int = 2) -> list[tuple]:
    return [(k, p, bonus) for k in classes for p in props]


_FIGHTER_BLOCK = [
    "Harcos", "Abasziszi_Falanxharcos",
    "Dwoon_Vrtes_gyalogos", "Dwoon_Feher_lovas",
    "Ereni_Kekkopenyes",
    "Erigowi_Szabad_Lovas", "Erigowi_Talpas", "Erigowi_Ijasz",
    "Gianagi_Alabardos",
    "Haonwell_Alborne_Csillag", "Haonwell_Nerton",
    "Ilanori_Vagtato", "Sirenari_Erdjaro", "Torpe_Harcos",
    "Rackla_lovas", "Tiadlani_Kardmester",
    "Toroni_Ezustkard_Bajnok", "Toroni_Elitharcos",
    "Predoci_Vrtes", "Edorli_Gyalogos", "Harcos_tengerszek",
    "Praedarmon_Lobogoi", "Syburri_Vrtesgyalogos",
    "Nasti_konnyulovas", "Ordani_langro",
    "Hadzsi", "Bahrada", "Birodalmi_zsoldosok",
    "Gorvik_Szabad_harcos", "Gorvik_Tengeri_vadasz",
    "Krani_Szabados",
    "Yllinori_Solyom", "Yllinori_Kopjas_Farkas", "Yllinori_Vaslovas",
    "Yllinori_Medve", "Yllinori_Sas",
    "Gladiator",
]

_PAP_BLOCK_AKER_ASZTR = [
    "Pap",
    "Alborne_pap", "Antoh_pap",
    "Arel_pap_Solyomsziv", "Arel_pap_Solyomkarom",
    "Darton_pap", "Della_pap", "Doldzsah_pap", "Domvik_pap",
    "Dreina_pap_Pol", "Dreina_pap_Gazd", "Dreina_pap_Jog",
    "Dzsah_pap", "Ellana_papno",
    "Galradzsa_pap", "Gilron_pap_Mernok", "Gilron_pap_Seged",
    "Krad_pap", "Kyel_pap",
    "Morgena_pap_Angyal", "Morgena_pap_Farkas",
    "Noir_pap_Befogadott", "Noir_pap_Balvanytagado",
    "Orwella_Papno_ANH", "Orwella_Papno_PE",
    "Ranil_pap",
    "Saman_pap_Leutaril", "Saman_pap_Ramkir", "Saman_pap_Tomatis",
    "Sogron_pap_Langvihar", "Sogron_pap_Urai",
    "Tharr_pap_Khotorr", "Tharr_pap_Sanquinator",
    "Kadal_pap",
    "Szerzetes_Benignus", "Tuz_Taplo", "Nomad_saman",
]

_PAPLOVAG_ERO_BLOCK = [
    "Paplovag",
    "Darton_paplovag", "Dervis", "Domvik_bosz_vadasz", "Domvik_paplovag",
    "Dreina_paplovag", "Krad_paplovag", "Orwella_paplovag",
    "Ranil_paplovag", "Uwel_paplovag",
]

_SPEC_KEPZETES: list[tuple] = (
    # Fighter block: erő, állóképesség, gyorsaság, ügyesség
    _kf(_FIGHTER_BLOCK, ["ero", "allokepesseg", "gyorsasag", "ugyesseg"])
    # Individual warriors
    + _kf(["Barbar"],          ["ero"])
    + _kf(["Bajvivo", "Tolvaj"], ["gyorsasag", "ugyesseg"])
    + _kf(["Fejvadasz"],       ["allokepesseg", "gyorsasag"])
    + _kf(["Lovag"],           ["ero", "allokepesseg", "szepseg"])
    + _kf(["Fonix"],           ["ero"])
    # Bárd / Sötét_Bárd
    + _kf(["Bard", "Sotet_Bard"], ["gyorsasag", "intelligencia"])
    # Mágikus
    + _kf(["Kardmuvesz"],          ["gyorsasag"])
    + _kf(["Boszorkany"],          ["asztral"])
    + _kf(["Boszorkanymester"],    ["ugyesseg"])
    + _kf(["Varazslo"],            ["intelligencia", "akarateroe", "asztral"])
    + _kf(["Szerzetes_Pyarronita"], ["intelligencia"])
    # Papok: akarateroe + asztrál
    + _kf(_PAP_BLOCK_AKER_ASZTR, ["akarateroe", "asztral"])
    # Kivételek a papok közül
    + _kf(["Adron_pap"],              ["akarateroe"])
    + _kf(["Arel_pap_Solyomcsor"],    ["asztral"])
    + _kf(["Ranagol_pap", "Ranagol_paplovag"], ["intelligencia", "asztral"])
    + _kf(["Tharr_pap_Quessor"],      ["ero", "intelligencia", "akarateroe", "asztral"])
    + _kf(["Tooma_pap"],              ["ero", "akarateroe", "asztral"])
    # Paplovag blokk
    + _kf(_PAPLOVAG_ERO_BLOCK, ["ero"])
)


def _seed_spec_kepzetes(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM kaszt_spec_kepzetes")
    kaszt_lookup = {r["nev"]: r["id"] for r in conn.execute("SELECT id, nev FROM kasztok").fetchall()}

    inserted, skipped = 0, []
    for kaszt_nev, tulajdonsag, max_bonus in _SPEC_KEPZETES:
        kaszt_id = kaszt_lookup.get(kaszt_nev)
        if kaszt_id is None:
            skipped.append(kaszt_nev)
            continue
        conn.execute(
            "INSERT OR REPLACE INTO kaszt_spec_kepzetes (kaszt_id, tulajdonsag, max_bonus) VALUES (?,?,?)",
            (kaszt_id, tulajdonsag, max_bonus),
        )
        inserted += 1

    if skipped:
        print(f"  WARNING spec_kepzetes: ismeretlen kasztok: {sorted(set(skipped))}")


def _seed_codes(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO codes (code_type, code_no, ertek, leiras) VALUES (?, ?, ?, ?)
        ON CONFLICT(code_type, code_no) DO UPDATE SET ertek=excluded.ertek, leiras=excluded.leiras
        """,
        _CODES,
    )


def _seed_skills(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM kepzettsegek")
    conn.executemany(
        """
        INSERT INTO kepzettsegek (id, nev, kategoria, tipus, ar_alapfok, ar_mesterfok)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        _SKILLS,
    )


# ---------------------------------------------------------------------------
# Manual corrections (JSON errors or data missing from source)
# ---------------------------------------------------------------------------

_PATCHES: list[tuple[str, tuple]] = [
    # Amazon: JSON has alap_kp=8/kp_per_szint=0, correct is 0/8
    ("UPDATE kasztok SET alap_kp=0, kp_per_szint=8 WHERE nev=?", ("Amazon",)),
    # Barbar: JSON missing kotelezo_hm_ve, correct is 3
    ("UPDATE kasztok SET kotelezo_hm_ve=3 WHERE nev=?", ("Barbar",)),
    # Mana per szint (not in JSON)
    ("UPDATE kasztok SET mana_per_szint=8  WHERE nev=?", ("Boszorkany",)),
    ("UPDATE kasztok SET mana_per_szint=6  WHERE nev=?", ("Tuzvarazslo",)),
    ("UPDATE kasztok SET mana_per_szint=10 WHERE nev=?", ("Varazslo",)),
    ("UPDATE kasztok SET mana_per_szint=7  WHERE nev=?", ("Boszorkanymester",)),
    ("UPDATE kasztok SET mana_per_szint=9  WHERE nev=?", ("Pap",)),
    ("UPDATE kasztok SET mana_per_szint=9  WHERE nev=?", ("Paplovag",)),
    ("UPDATE kasztok SET mana_per_szint=5  WHERE nev=?", ("Bard",)),
    # HM elosztási mód (kivételek; default=1)
    ("UPDATE kasztok SET hm_elosztasi_mod=3 WHERE nev=?", ("Boszorkany",)),
    ("UPDATE kasztok SET hm_elosztasi_mod=3 WHERE nev=?", ("Varazslo",)),
    ("UPDATE kasztok SET hm_elosztasi_mod=2 WHERE nev=?", ("Boszorkanymester",)),
    ("UPDATE kasztok SET hm_elosztasi_mod=4 WHERE nev=?", ("Tolvaj",)),
    ("UPDATE kasztok SET hm_elosztasi_mod=4 WHERE nev=?", ("Lovag",)),
    # Szazalek per szint (freely distributed among szazalekos skills each level)
    ("UPDATE kasztok SET szazalek_per_szint=20 WHERE nev=?", ("Harcos",)),
    ("UPDATE kasztok SET szazalek_per_szint=15 WHERE nev=?", ("Gladiator",)),
    ("UPDATE kasztok SET szazalek_per_szint=20 WHERE nev=?", ("Fejvadasz",)),
    ("UPDATE kasztok SET szazalek_per_szint=62 WHERE nev=?", ("Tolvaj",)),
    ("UPDATE kasztok SET szazalek_per_szint=45 WHERE nev=?", ("Bard",)),
    ("UPDATE kasztok SET szazalek_per_szint=22 WHERE nev=?", ("Harcmuvesz",)),
    ("UPDATE kasztok SET szazalek_per_szint=18 WHERE nev=?", ("Kardmuvesz",)),
    ("UPDATE kasztok SET szazalek_per_szint=15 WHERE nev=?", ("Boszorkanymester",)),
]


# ---------------------------------------------------------------------------
# Class skill grants
# (kaszt_db_nev, kepzettseg_nev, szint_tol, fok, szazalek)
# fok: 'alap'|'mester'|'kyr'|'slan'  for regular skills and Pszi
#      '1'..'5'|'mester'              for Nyelvtudás
# szazalek: starting % for szazalekos skills, None for alap_mester skills
# ---------------------------------------------------------------------------

_CLASS_SKILLS: list[tuple] = [
    # ===== HARCOS =====
    ("Harcos", "Fegyverhasználat",           0,  "alap",   None),
    ("Harcos", "Fegyverhasználat",           0,  "alap",   None),
    ("Harcos", "Fegyverhasználat",           0,  "alap",   None),
    ("Harcos", "Úszás",                      0,  "alap",   None),
    ("Harcos", "Lovaglás",                   0,  "alap",   None),
    ("Harcos", "Futás",                      0,  "alap",   None),
    ("Harcos", "Mászás",                     0,  "alap",   15),
    ("Harcos", "Esés",                       0,  "alap",   20),
    ("Harcos", "Ugrás",                      0,  "alap",   10),
    ("Harcos", "Hadvezetés",                 6,  "alap",   None),
    # ===== GLADIÁTOR =====
    ("Gladiator", "Birkózás",               0,  "alap",   None),
    ("Gladiator", "Ökölharc",               0,  "alap",   None),
    ("Gladiator", "Kétkezes harc",          0,  "alap",   None),
    ("Gladiator", "Nehézvért viselet",       0,  "alap",   None),
    ("Gladiator", "Pajzs használata",        0,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        0,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        0,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        0,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        0,  "alap",   None),
    ("Gladiator", "Fegyvertörés",            0,  "alap",   None),
    ("Gladiator", "Esés",                    0,  "alap",   0),
    ("Gladiator", "Ugrás",                   0,  "alap",   0),
    ("Gladiator", "Fegyverhasználat",        2,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        4,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        4,  "mester", None),
    ("Gladiator", "Kétkezes harc",           5,  "mester", None),
    ("Gladiator", "Vakharc",                 6,  "alap",   None),
    ("Gladiator", "Fegyverhasználat",        7,  "alap",   None),
    ("Gladiator", "Pajzs használata",        7,  "mester", None),
    ("Gladiator", "Fegyvertörés",            9,  "mester", None),
    # ===== FEJVADÁSZ =====
    ("Fejvadasz", "Ökölharc",                0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverismeret",          0,  "alap",   None),
    ("Fejvadasz", "Fegyverdobás",            0,  "alap",   None),
    ("Fejvadasz", "Fegyverdobás",            0,  "alap",   None),
    ("Fejvadasz", "Fegyverdobás",            0,  "alap",   None),
    ("Fejvadasz", "Pszi",                    0,  "alap",   None),
    ("Fejvadasz", "Úszás",                   0,  "alap",   None),
    ("Fejvadasz", "Futás",                   0,  "alap",   None),
    ("Fejvadasz", "Csapdaállítás",           0,  "alap",   None),
    ("Fejvadasz", "Álcázás/álruha",          0,  "alap",   None),
    ("Fejvadasz", "Hátbaszúrás",             0,  "alap",   None),
    ("Fejvadasz", "Mászás",                  0,  "alap",   30),
    ("Fejvadasz", "Esés",                    0,  "alap",   15),
    ("Fejvadasz", "Ugrás",                   0,  "alap",   15),
    ("Fejvadasz", "Lopózás",                 0,  "alap",   20),
    ("Fejvadasz", "Rejtőzködés",             0,  "alap",   25),
    ("Fejvadasz", "Csapdafelfedezés",        0,  "alap",   10),
    ("Fejvadasz", "Kötélből szabadulás",     2,  "alap",   None),
    ("Fejvadasz", "Ökölharc",                2,  "mester", None),
    ("Fejvadasz", "Vakharc",                 3,  "alap",   None),
    ("Fejvadasz", "Nyomolvasás/eltűntetés",  4,  "alap",   None),
    ("Fejvadasz", "Álcázás/álruha",          4,  "mester", None),
    ("Fejvadasz", "Pszi",                    5,  "mester", None),
    ("Fejvadasz", "Vakharc",                 7,  "mester", None),
    ("Fejvadasz", "Kötélből szabadulás",     8,  "mester", None),
    ("Fejvadasz", "Nyomolvasás/eltűntetés",  9,  "mester", None),
    # ===== LOVAG =====
    ("Lovag", "Nehézvért viselet",           0,  "mester", None),
    ("Lovag", "Pajzs használata",            0,  "alap",   None),
    ("Lovag", "Fegyverhasználat",            0,  "alap",   None),
    ("Lovag", "Fegyverhasználat",            0,  "alap",   None),
    ("Lovag", "Fegyverhasználat",            0,  "alap",   None),
    ("Lovag", "Fegyverhasználat",            0,  "alap",   None),
    ("Lovag", "Fegyverhasználat",            0,  "alap",   None),
    ("Lovag", "Fegyverismeret",              0,  "alap",   None),
    ("Lovag", "Hadvezetés",                  0,  "alap",   None),
    ("Lovag", "Etikett",                     0,  "alap",   None),
    ("Lovag", "Lovaglás",                    0,  "mester", None),
    ("Lovag", "Nyelvtudás",                  0,  "4",      None),
    ("Lovag", "Nyelvtudás",                  0,  "2",      None),
    ("Lovag", "Nyelvtudás",                  0,  "2",      None),
    ("Lovag", "Nyelvtudás",                  0,  "2",      None),
    ("Lovag", "Írás/olvasás",                0,  "alap",   None),
    ("Lovag", "Heraldika",                   0,  "alap",   None),
    ("Lovag", "Heraldika",                   3,  "mester", None),
    ("Lovag", "Pajzs használata",            4,  "mester", None),
    ("Lovag", "Pszi",                        4,  "alap",   None),
    ("Lovag", "Sebgyógyítás",                4,  "alap",   None),
    ("Lovag", "Fegyverhasználat",            5,  "mester", None),
    ("Lovag", "Hadvezetés",                  9,  "mester", None),
    ("Lovag", "Pszi",                        12, "mester", None),
    # ===== TOLVAJ =====
    ("Tolvaj", "Fegyverhasználat",           0,  "alap",   None),
    ("Tolvaj", "Fegyverhasználat",           0,  "alap",   None),
    ("Tolvaj", "Fegyverdobás",               0,  "alap",   None),
    ("Tolvaj", "Nyelvtudás",                 0,  "3",      None),
    ("Tolvaj", "Nyelvtudás",                 0,  "2",      None),
    ("Tolvaj", "Nyelvtudás",                 0,  "2",      None),
    ("Tolvaj", "Értékbecslés",               0,  "alap",   None),
    ("Tolvaj", "Kocsmai verekedés",          0,  "alap",   None),
    ("Tolvaj", "Mászás",                     0,  "alap",   45),
    ("Tolvaj", "Esés",                       0,  "alap",   15),
    ("Tolvaj", "Zárnyitás",                  0,  "alap",   25),
    ("Tolvaj", "Ugrás",                      0,  "alap",   10),
    ("Tolvaj", "Lopózás",                    0,  "alap",   30),
    ("Tolvaj", "Rejtőzködés",                0,  "alap",   15),
    ("Tolvaj", "Kötéltánc",                  0,  "alap",   25),
    ("Tolvaj", "Zsebmetszés",                0,  "alap",   35),
    ("Tolvaj", "Csapdafelfedezés",           0,  "alap",   25),
    ("Tolvaj", "Titkosajtó keresés",         0,  "alap",   15),
    ("Tolvaj", "Kötélből szabadulás",        2,  "alap",   None),
    ("Tolvaj", "Csomózás",                   3,  "alap",   None),
    ("Tolvaj", "Hátbaszúrás",                3,  "alap",   None),
    ("Tolvaj", "Kocsmai verekedés",          4,  "mester", None),
    ("Tolvaj", "Fegyverdobás",               5,  "mester", None),
    # ===== BÁRD =====
    ("Bard", "Fegyverhasználat",             0,  "alap",   None),
    ("Bard", "Fegyverhasználat",             0,  "alap",   None),
    ("Bard", "Fegyverhasználat",             0,  "alap",   None),
    ("Bard", "Fegyverhasználat",             0,  "alap",   None),
    ("Bard", "Fegyverdobás",                 0,  "alap",   None),
    ("Bard", "Nyelvtudás",                   0,  "2",      None),
    ("Bard", "Nyelvtudás",                   0,  "2",      None),
    ("Bard", "Nyelvtudás",                   0,  "3",      None),
    ("Bard", "Nyelvtudás",                   0,  "4",      None),
    ("Bard", "Nyelvtudás",                   0,  "5",      None),
    ("Bard", "Pszi",                         0,  "alap",   None),
    ("Bard", "Írás/olvasás",                 0,  "alap",   None),
    ("Bard", "Legendaismeret",               0,  "mester", None),
    ("Bard", "Etikett",                      0,  "alap",   None),
    ("Bard", "Lovaglás",                     0,  "alap",   None),
    ("Bard", "Szexuális kultúra",            0,  "alap",   None),
    ("Bard", "Éneklés/zenélés",              0,  "alap",   None),
    ("Bard", "Hangutánzás",                  0,  "alap",   None),
    ("Bard", "Hamiskártya",                  0,  "alap",   None),
    ("Bard", "Mászás",                       0,  "alap",   25),
    ("Bard", "Esés",                         0,  "alap",   5),
    ("Bard", "Ugrás",                        0,  "alap",   10),
    ("Bard", "Lopózás",                      0,  "alap",   20),
    ("Bard", "Rejtőzködés",                  0,  "alap",   10),
    ("Bard", "Kötéltánc",                    0,  "alap",   5),
    ("Bard", "Zsebmetszés",                  0,  "alap",   5),
    ("Bard", "Csapdafelfedezés",             0,  "alap",   10),
    ("Bard", "Titkosajtó keresés",           0,  "alap",   5),
    ("Bard", "Értékbecslés",                 2,  "alap",   None),
    ("Bard", "Zsonglőrködés",                2,  "alap",   None),
    ("Bard", "Kocsmai verekedés",            2,  "alap",   None),
    ("Bard", "Ökölharc",                     3,  "alap",   None),
    ("Bard", "Csomózás",                     3,  "alap",   None),
    ("Bard", "Tánc",                         3,  "alap",   None),
    ("Bard", "Kocsmai verekedés",            4,  "mester", None),
    ("Bard", "Fegyverdobás",                 4,  "mester", None),
    ("Bard", "Kötélből szabadulás",          4,  "alap",   None),
    ("Bard", "Etikett",                      4,  "alap",   None),
    ("Bard", "Hamiskártya",                  5,  "mester", None),
    ("Bard", "Pszi",                         5,  "mester", None),
    ("Bard", "Hátbaszúrás",                  6,  "alap",   None),
    ("Bard", "Szexuális kultúra",            7,  "mester", None),
    ("Bard", "Hangutánzás",                  8,  "mester", None),
    # ===== HARCMŰVÉSZ =====
    ("Harcmuvesz", "Vakharc",                0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Harcmuvesz", "Fegyverdobás",           0,  "alap",   None),
    ("Harcmuvesz", "Fegyverdobás",           0,  "alap",   None),
    ("Harcmuvesz", "Fegyverdobás",           0,  "alap",   None),
    ("Harcmuvesz", "Fegyverdobás",           0,  "alap",   None),
    ("Harcmuvesz", "Fegyvertörés",           0,  "alap",   None),
    ("Harcmuvesz", "Pszi",                   0,  "slan",   None),
    ("Harcmuvesz", "Lovaglás",               0,  "alap",   None),
    ("Harcmuvesz", "Úszás",                  0,  "alap",   None),
    ("Harcmuvesz", "Futás",                  0,  "alap",   None),
    ("Harcmuvesz", "Mászás",                 0,  "alap",   20),
    ("Harcmuvesz", "Esés",                   0,  "alap",   35),
    ("Harcmuvesz", "Ugrás",                  0,  "alap",   30),
    ("Harcmuvesz", "Sebgyógyítás",           2,  "alap",   None),
    ("Harcmuvesz", "Fegyvertörés",           4,  "alap",   None),
    ("Harcmuvesz", "Vakharc",                5,  "mester", None),
    ("Harcmuvesz", "Sebgyógyítás",           6,  "mester", None),
    # ===== KARDMŰVÉSZ =====
    ("Kardmuvesz", "Ökölharc",               0,  "alap",   None),
    ("Kardmuvesz", "Birkózás",               0,  "alap",   None),
    ("Kardmuvesz", "Vakharc",                0,  "alap",   None),
    ("Kardmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Kardmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Kardmuvesz", "Fegyverhasználat",       0,  "alap",   None),
    ("Kardmuvesz", "Fegyvertörés",           0,  "alap",   None),
    ("Kardmuvesz", "Pszi",                   0,  "slan",   None),
    ("Kardmuvesz", "Hadvezetés",             0,  "alap",   None),
    ("Kardmuvesz", "Etikett",                0,  "alap",   None),
    ("Kardmuvesz", "Lovaglás",               0,  "alap",   None),
    ("Kardmuvesz", "Úszás",                  0,  "alap",   None),
    ("Kardmuvesz", "Futás",                  0,  "alap",   None),
    ("Kardmuvesz", "Mászás",                 0,  "alap",   10),
    ("Kardmuvesz", "Esés",                   0,  "alap",   20),
    ("Kardmuvesz", "Ugrás",                  0,  "alap",   10),
    ("Kardmuvesz", "Lovaglás",               3,  "mester", None),
    ("Kardmuvesz", "Fegyvertörés",           4,  "mester", None),
    ("Kardmuvesz", "Vakharc",                5,  "mester", None),
    ("Kardmuvesz", "Fegyverhasználat",       5,  "mester", None),
    # ===== BOSZORKÁNY =====
    ("Boszorkany", "Fegyverhasználat",       0,  "alap",   None),
    ("Boszorkany", "Fegyverdobás",           0,  "alap",   None),
    ("Boszorkany", "Pszi",                   0,  "mester", None),
    ("Boszorkany", "Nyelvtudás",             0,  "3",      None),
    ("Boszorkany", "Nyelvtudás",             0,  "2",      None),
    ("Boszorkany", "Herbalizmus",            0,  "alap",   None),
    ("Boszorkany", "Írás/olvasás",           0,  "alap",   None),
    ("Boszorkany", "Méregkeverés/semlegesítés", 0, "alap", None),
    ("Boszorkany", "Sebgyógyítás",           0,  "alap",   None),
    ("Boszorkany", "Szexuális kultúra",      0,  "alap",   None),
    ("Boszorkany", "Méregkeverés/semlegesítés", 4, "mester", None),
    ("Boszorkany", "Herbalizmus",            5,  "mester", None),
    # ===== BOSZORKÁNYMESTER =====
    ("Boszorkanymester", "Fegyverhasználat", 0,  "alap",   None),
    ("Boszorkanymester", "Fegyverhasználat", 0,  "alap",   None),
    ("Boszorkanymester", "Fegyverhasználat", 0,  "alap",   None),
    ("Boszorkanymester", "Fegyverdobás",     0,  "alap",   None),
    ("Boszorkanymester", "Pszi",             0,  "mester", None),
    ("Boszorkanymester", "Nyelvtudás",       0,  "3",      None),
    ("Boszorkanymester", "Nyelvtudás",       0,  "3",      None),
    ("Boszorkanymester", "Nyelvtudás",       0,  "2",      None),
    ("Boszorkanymester", "Írás/olvasás",     0,  "alap",   None),
    ("Boszorkanymester", "Álcázás/álruha",   0,  "alap",   None),
    ("Boszorkanymester", "Méregkeverés/semlegesítés", 0, "alap", None),
    ("Boszorkanymester", "Lopózás",          0,  "alap",   15),
    ("Boszorkanymester", "Rejtőzködés",      0,  "alap",   15),
    ("Boszorkanymester", "Hátbaszúrás",      2,  "alap",   None),
    ("Boszorkanymester", "Méregkeverés/semlegesítés", 4, "mester", None),
    ("Boszorkanymester", "Hátbaszúrás",      5,  "mester", None),
    ("Boszorkanymester", "Herbalizmus",      6,  "mester", None),
    # ===== TŰZVARÁZSLÓ =====
    ("Tuzvarazslo", "Fegyverhasználat",      0,  "alap",   None),
    ("Tuzvarazslo", "Fegyverhasználat",      0,  "alap",   None),
    ("Tuzvarazslo", "Pszi",                  0,  "mester", None),
    ("Tuzvarazslo", "Írás/olvasás",          0,  "alap",   None),
    ("Tuzvarazslo", "Nyelvtudás",            0,  "4",      None),
    ("Tuzvarazslo", "Nyelvtudás",            0,  "3",      None),
    ("Tuzvarazslo", "Lovaglás",              0,  "alap",   None),
    ("Tuzvarazslo", "Hajózás",               0,  "alap",   None),
    # ===== VARÁZSLÓ =====
    ("Varazslo", "Fegyverhasználat",         0,  "alap",   None),
    ("Varazslo", "Pszi",                     0,  "kyr",    None),
    ("Varazslo", "Nyelvtudás",               0,  "5",      None),
    ("Varazslo", "Nyelvtudás",               0,  "4",      None),
    ("Varazslo", "Ősi nyelv ismerete",       0,  "alap",   None),
    ("Varazslo", "Alkímia",                  0,  "alap",   None),
    ("Varazslo", "Írás/olvasás",             0,  "alap",   None),
    ("Varazslo", "Sebgyógyítás",             0,  "alap",   None),
    ("Varazslo", "Élettan",                  0,  "alap",   None),
    ("Varazslo", "Legendaismeret",           0,  "alap",   None),
    ("Varazslo", "Történelemismeret",        0,  "alap",   None),
    ("Varazslo", "Rúnamágia",                0,  "alap",   None),
    ("Varazslo", "Herbalizmus",              4,  "alap",   None),
    ("Varazslo", "Alkímia",                  6,  "mester", None),
    ("Varazslo", "Rúnamágia",                6,  "mester", None),
    ("Varazslo", "Legendaismeret",           7,  "mester", None),
    ("Varazslo", "Történelemismeret",        8,  "mester", None),
]

# ---------------------------------------------------------------------------
# Pap (priest) class skills
# Base package → "Pap"; religion-specific → variant class.
# Engine should merge both when generating a priest NPC.
# ---------------------------------------------------------------------------

_PAP_BASE = [
    ("Fegyverhasználat",  0,  "alap",   None),
    ("Pszi",              0,  "mester", None),
    ("Nyelvtudás",        0,  "5",      None),
    ("Nyelvtudás",        0,  "5",      None),
    ("Írás/olvasás",      0,  "alap",   None),
    ("Vallásismeret",     0,  "mester", None),
    ("Történelemismeret", 0,  "mester", None),
    ("Éneklés/zenélés",   0,  "alap",   None),
]

_AREL_PAP = [
    ("Fegyverhasználat",         0,  "alap",   None),
    ("Fegyverhasználat",         0,  "alap",   None),
    ("Fegyverhasználat",         0,  "alap",   None),
    ("Fegyverdobás",             0,  "alap",   None),
    ("Fegyverismeret",           0,  "alap",   None),
    ("Nyelvtudás",               0,  "4",      None),
    ("Nyelvtudás",               0,  "3",      None),
    ("Nyelvtudás",               0,  "2",      None),
    ("Időjóslás",                0,  "alap",   None),
    ("Herbalizmus",              0,  "alap",   None),
    ("Sebgyógyítás",             0,  "alap",   None),
    ("Lovaglás",                 0,  "alap",   None),
    ("Vadászat/halászat",        0,  "mester", None),
    ("Erdőjárás",                0,  "mester", None),
    ("Idomítás",                 0,  "alap",   None),
    ("Kocsmai verekedés",        2,  "alap",   None),
    ("Legendaismeret",           3,  "alap",   None),
    ("Csapdaállítás",            4,  "alap",   None),
    ("Nyomolvasás/eltűntetés",   5,  "alap",   None),
    ("Fegyverhasználat",         9,  "mester", None),
]

_DOMVIK_PAP = [
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Pajzs használata",          0,  "alap",   None),
    ("Ősi nyelv ismerete",        0,  "alap",   None),
    ("Írás/olvasás",              0,  "mester", None),
    ("Sebgyógyítás",              0,  "mester", None),
    ("Méregkeverés/semlegesítés", 0,  "alap",   None),
    ("Heraldika",                 0,  "alap",   None),
    ("Lovaglás",                  0,  "alap",   None),
    ("Ősi nyelv ismerete",        3,  "mester", None),
    ("Méregkeverés/semlegesítés", 3,  "mester", None),
]

_RANAGOL_PAP = [
    ("Hátbaszúrás",               0,  "alap",   None),
    ("Mágia használat",           3,  "alap",   None),
    ("Hátbaszúrás",               5,  "mester", None),
    ("Ősi nyelv ismerete",        5,  "alap",   None),
    ("Mágia használat",           6,  "mester", None),
    ("Ősi nyelv ismerete",        11, "mester", None),
]

_KYEL_PAP = [
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Pajzs használata",          0,  "alap",   None),
    ("Nehézvért viselet",         0,  "alap",   None),
    ("Fegyverismeret",            0,  "alap",   None),
    ("Hadvezetés",                0,  "alap",   None),
    ("Nyelvtudás",                0,  "3",      None),
    ("Nyelvtudás",                0,  "2",      None),
    ("Nyelvtudás",                0,  "2",      None),
    ("Sebgyógyítás",              0,  "alap",   None),
    ("Herbalizmus",               0,  "alap",   None),
    ("Lefegyverzés",              0,  "alap",   None),
    ("Etikett",                   0,  "mester", None),
    ("Térképészet",               3,  "alap",   None),
    ("Sebgyógyítás",              4,  "mester", None),
    ("Herbalizmus",               5,  "mester", None),
    ("Élettan",                   6,  "alap",   None),
    ("Lefegyverzés",              7,  "mester", None),
]

_THARR_PAP = [
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Fegyverhasználat",          0,  "alap",   None),
    ("Fegyverdobás",              0,  "alap",   None),
    ("Ősi nyelv ismerete",        0,  "mester", None),
    ("Méregkeverés/semlegesítés", 0,  "alap",   None),
    ("Hátbaszúrás",               0,  "alap",   None),
    ("Alkímia",                   0,  "alap",   None),
    ("Demonológia",               0,  "alap",   None),
    ("Alkímia",                   3,  "mester", None),
    ("Demonológia",               4,  "mester", None),
    ("Rúnamágia",                 6,  "alap",   None),
]

for _s in _PAP_BASE:
    _CLASS_SKILLS.append(("Pap",) + _s)
for _k in ["Arel_pap_Solyomcsor", "Arel_pap_Solyomkarom", "Arel_pap_Solyomsziv"]:
    for _s in _AREL_PAP: _CLASS_SKILLS.append((_k,) + _s)
for _s in _DOMVIK_PAP:
    _CLASS_SKILLS.append(("Domvik_pap",) + _s)
for _s in _RANAGOL_PAP:
    _CLASS_SKILLS.append(("Ranagol_pap",) + _s)
for _s in _KYEL_PAP:
    _CLASS_SKILLS.append(("Kyel_pap",) + _s)
for _k in ["Tharr_pap_Khotorr", "Tharr_pap_Quessor", "Tharr_pap_Sanquinator"]:
    for _s in _THARR_PAP: _CLASS_SKILLS.append((_k,) + _s)

# ---------------------------------------------------------------------------
# Paplovag (paladin) class skills
# ---------------------------------------------------------------------------

_PAPLOVAG_BASE = [
    ("Nehézvért viselet",  0,  "mester", None),
    ("Pajzs használata",   0,  "alap",   None),
    ("Fegyverhasználat",   0,  "alap",   None),
    ("Fegyverhasználat",   0,  "alap",   None),
    ("Fegyverhasználat",   0,  "alap",   None),
    ("Fegyverhasználat",   0,  "alap",   None),
    ("Hadvezetés",         0,  "alap",   None),
    ("Pszi",               0,  "mester", None),
    ("Nyelvtudás",         0,  "5",      None),
    ("Nyelvtudás",         0,  "4",      None),
    ("Írás/olvasás",       0,  "alap",   None),
    ("Vallásismeret",      0,  "alap",   None),
    ("Történelemismeret",  0,  "alap",   None),
    ("Heraldika",          0,  "alap",   None),
    ("Etikett",            0,  "alap",   None),
    ("Lovaglás",           0,  "mester", None),
    ("Éneklés/zenélés",    0,  "alap",   None),
    ("Vallásismeret",      5,  "mester", None),
    ("Pajzs használata",   5,  "mester", None),
    ("Fegyverhasználat",   7,  "mester", None),
]

_KRAD_PAPLOVAG = [
    ("Nyelvtudás",         0,  "3",      None),
    ("Nyelvtudás",         0,  "3",      None),
    ("Nyelvtudás",         0,  "3",      None),
    ("Nyelvtudás",         0,  "3",      None),
    ("Herbalizmus",        0,  "alap",   None),
    ("Történelemismeret",  0,  "alap",   None),
    ("Erdőjárás",          0,  "alap",   None),
    ("Úszás",              0,  "alap",   None),
    ("Térképészet",        0,  "alap",   None),
    ("Legendaismeret",     0,  "alap",   None),
    ("Legendaismeret",     5,  "mester", None),
    ("Történelemismeret",  5,  "mester", None),
]

_DARTON_PAPLOVAG = [
    ("Birkózás",                  0,  "alap",   None),
    ("Fegyvertörés",              0,  "alap",   None),
    ("Méregkeverés/semlegesítés", 0,  "alap",   None),
    ("Csapdaállítás",             0,  "alap",   None),
    ("Kocsmai verekedés",         0,  "alap",   None),
    ("Hamiskártya",               0,  "alap",   None),
    ("Kocsmai verekedés",         3,  "mester", None),
    ("Idomítás",                  3,  "alap",   None),
    ("Hamiskártya",               4,  "mester", None),
    ("Kétkezes harc",             4,  "mester", None),
    ("Hátbaszúrás",               7,  "alap",   None),
]

_DOMVIK_PAPLOVAG = [
    ("Sebgyógyítás",              0,  "alap",   None),
    ("Ősi nyelv ismerete",        0,  "alap",   None),
    ("Ősi nyelv ismerete",        4,  "mester", None),
]

_RANAGOL_PAPLOVAG = [
    ("Fegyverdobás",              0,  "alap",   None),
    ("Ősi nyelv ismerete",        0,  "alap",   None),
    ("Hátbaszúrás",               0,  "alap",   None),
    ("Méregkeverés/semlegesítés", 3,  "alap",   None),
    ("Hátbaszúrás",               6,  "mester", None),
]

_DREINA_PAPLOVAG = [
    ("Történelemismeret",  0,  "alap",   None),
    ("Hadvezetés",         0,  "mester", None),
    ("Térképészet",        0,  "alap",   None),
    ("Heraldika",          0,  "mester", None),
    ("Történelemismeret",  4,  "mester", None),
]

_UWEL_PAPLOVAG = [
    ("Pajzs használata",          0,  "mester", None),
    ("Fegyvertörés",              0,  "alap",   None),
    ("Lefegyverzés",              0,  "alap",   None),
    ("Nyomolvasás/eltűntetés",    3,  "mester", None),
    ("Herbalizmus",               5,  "alap",   None),
    ("Sebgyógyítás",              5,  "mester", None),
]

for _s in _PAPLOVAG_BASE:    _CLASS_SKILLS.append(("Paplovag",) + _s)
for _s in _KRAD_PAPLOVAG:    _CLASS_SKILLS.append(("Krad_paplovag",) + _s)
for _s in _DARTON_PAPLOVAG:  _CLASS_SKILLS.append(("Darton_paplovag",) + _s)
for _s in _DOMVIK_PAPLOVAG:  _CLASS_SKILLS.append(("Domvik_paplovag",) + _s)
for _s in _RANAGOL_PAPLOVAG: _CLASS_SKILLS.append(("Ranagol_paplovag",) + _s)
for _s in _DREINA_PAPLOVAG:  _CLASS_SKILLS.append(("Dreina_paplovag",) + _s)
for _s in _UWEL_PAPLOVAG:    _CLASS_SKILLS.append(("Uwel_paplovag",) + _s)

# ---------------------------------------------------------------------------
# Amazon, Barbar, Bajvivo
# ---------------------------------------------------------------------------

for _s in [
    # Fegyverhasználat: hosszúkard, tőr, íj, dárda
    ("Fegyverhasználat",         0,  "alap",   None),  # hosszúkard
    ("Fegyverhasználat",         0,  "alap",   None),  # tőr
    ("Fegyverhasználat",         0,  "alap",   None),  # íj
    ("Fegyverhasználat",         0,  "alap",   None),  # dárda
    ("Fegyverdobás",             0,  "alap",   None),  # tőr
    ("Időjóslás",                0,  "alap",   None),
    ("Herbalizmus",              0,  "alap",   None),
    ("Nyomolvasás/eltűntetés",   0,  "alap",   None),
    ("Csapdaállítás",            0,  "alap",   None),
    ("Futás",                    0,  "alap",   None),
    ("Hangutánzás",              0,  "alap",   None),
    ("Erdőjárás",                0,  "mester", None),
    ("Vadászat/halászat",        0,  "mester", None),
    ("Lovaglás",                 0,  "mester", None),
    ("Szexuális kultúra",        0,  "mester", None),
    ("Harci láz",                0,  "mester", None),
]: _CLASS_SKILLS.append(("Amazon",) + _s)

for _s in [
    ("Birkózás",                 0,  "alap",   None),
    ("Ökölharc",                 0,  "alap",   None),
    ("Fegyverhasználat",         0,  "alap",   None),
    ("Fegyverhasználat",         0,  "alap",   None),
    ("Fegyverhasználat",         0,  "alap",   None),
    ("Fegyvertörés",             0,  "alap",   None),
    ("Időjóslás",                0,  "alap",   None),
    ("Futás",                    0,  "alap",   None),
    ("Erdőjárás",                0,  "mester", None),
    ("Vadászat/halászat",        0,  "mester", None),
    ("Esés",                     0,  "alap",   40),
    ("Ugrás",                    0,  "alap",   25),
]: _CLASS_SKILLS.append(("Barbar",) + _s)

for _s in [
    ("Fegyverhasználat",         0,  "alap",   None),  # tőrkard
    ("Lefegyverzés",             0,  "alap",   None),  # tőrkard
    ("Vakharc",                  0,  "alap",   None),
    ("Fegyverismeret",           0,  "mester", None),
    ("Írás/olvasás",             0,  "alap",   None),
    ("Pszi",                     0,  "alap",   None),
    ("Nyelvtudás",               0,  "mester", None),
    ("Nyelvtudás",               0,  "5",      None),
    ("Nyelvtudás",               0,  "5",      None),
    ("Heraldika",                0,  "mester", None),
    ("Legendaismeret",           0,  "alap",   None),
    ("Történelemismeret",        0,  "alap",   None),
    ("Vallásismeret",            0,  "alap",   None),
    ("Etikett",                  0,  "mester", None),
    ("Lovaglás",                 0,  "alap",   None),
    ("Úszás",                    0,  "alap",   None),
    ("Szexuális kultúra",        0,  "alap",   None),
    ("Éneklés/zenélés",          0,  "alap",   None),
    ("Tánc",                     0,  "mester", None),
    ("Fegyverhasználat",         2,  "mester", None),  # tőrkard
    ("Lefegyverzés",             3,  "mester", None),  # tőrkard
    ("Vakharc",                  4,  "mester", None),
]: _CLASS_SKILLS.append(("Bajvivo",) + _s)


def _seed_class_skills(conn: sqlite3.Connection) -> None:
    skill_lookup  = {nev: sid for (sid, nev, *_) in _SKILLS}
    kaszt_lookup  = {r["nev"]: r["id"] for r in conn.execute("SELECT id, nev FROM kasztok").fetchall()}

    conn.execute("DELETE FROM kaszt_kepzettsegek")

    skipped: list[tuple] = []
    for (kaszt_nev, skill_nev, szint_tol, fok, szazalek) in _CLASS_SKILLS:
        kaszt_id  = kaszt_lookup.get(kaszt_nev)
        skill_id  = skill_lookup.get(skill_nev)
        if kaszt_id is None or skill_id is None:
            skipped.append((kaszt_nev, skill_nev))
            continue
        conn.execute(
            "INSERT INTO kaszt_kepzettsegek (kaszt_id, kepzettseg_id, szint_tol, fok, szazalek) VALUES (?,?,?,?,?)",
            (kaszt_id, skill_id, szint_tol, fok, szazalek),
        )

    if skipped:
        print(f"  WARNING: {len(skipped)} entries not found: {skipped}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def seed(db_path: Path = DB_PATH) -> None:
    init_db(db_path)

    with open(CLASSES_FILE, encoding="utf-8") as f:
        data = json.load(f)

    classes = data["kasztok"]
    conn = get_connection(db_path)
    try:
        for cls in classes:
            _seed_class(conn, cls)
        for sql, params in _PATCHES:
            conn.execute(sql, params)
        _seed_spec_kepzetes(conn)
        _seed_codes(conn)
        _seed_skills(conn)
        _seed_class_skills(conn)
        conn.commit()
        print(f"Seeded {len(classes)} classes, {len(_SKILLS)} skills, {len(_CLASS_SKILLS)} class-skill grants into {db_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
