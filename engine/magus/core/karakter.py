"""
MAGUS character persistence.

save_karakter        — write a character (from properties+combat modules) to DB
save_from_npc_result — write an NPC result (from npc_generator) to DB
load_karakter        — fetch by id, returns the full dict
row_to_npc           — convert a DB row to the NPC result shape the API returns
list_karakterek      — return summary rows for the list endpoint
update_karakter      — patch any columns of an existing character
delete_karakter      — remove a character by id
"""
from __future__ import annotations

import json
from pathlib import Path

from engine.magus.core.db import DB_PATH, get_connection

# JSON columns that hold lists — auto-serialised/deserialised
_JSON_COLS = {"tulajdonsagok", "harci_ertekek", "felszereles", "celok"}

# Combat stat keys worth persisting (final values + useful aggregates)
_COMBAT_KEYS = ("ke", "te", "ve", "ce", "kp", "ep", "fp",
                "szabad_hm_ossz", "szazalek_ossz", "fp_rolls")


def save_karakter(
    props_result: dict,
    combat_stats: dict,
    *,
    concept: dict | None = None,
    character: dict | None = None,
    db_path: Path = DB_PATH,
) -> int:
    """
    Persist a newly generated character.

    Args:
        props_result: output of generate_npc_properties()
        combat_stats: output of calculate_combat_stats()
        concept:   optional dict from npc_generator (race, role, ...)
        character: optional dict from npc_generator (name, appearance, ...)

    Returns:
        The new row id.
    """
    row: dict = {
        "kaszt":     props_result["kaszt"],
        "szint":     combat_stats["szint"],
        "njk_tipus": props_result["njk_tipus"],
        "tulajdonsagok": props_result["tulajdonsagok"],
        "harci_ertekek": {
            **{k: combat_stats[k] for k in _COMBAT_KEYS if k in combat_stats},
            "fp_formula":  combat_stats.get("fp_formula_str"),
            "kp_per_szint": combat_stats.get("alap_kp_per_szint"),
        },
    }

    if concept:
        row["faj"]   = concept.get("race")
        row["szerep"] = concept.get("role")

    if character:
        row["nev"]      = character.get("name")
        row["nem"]      = character.get("gender")
        row["kor_leiras"] = character.get("age_description")
        row["megjelenes"]  = character.get("appearance")
        row["szemelyiseg"] = character.get("personality")
        row["elotortenete"] = character.get("background")
        row["szolasmod"]   = character.get("speech_style")
        row["motivacio"]   = character.get("motivation")
        row["titok"]       = character.get("secret")
        row["idegenekhez_viszonyulas"] = character.get("attitude_to_strangers")

    serialized = {
        k: json.dumps(v, ensure_ascii=False) if k in _JSON_COLS else v
        for k, v in row.items()
        if v is not None
    }

    cols   = ", ".join(serialized.keys())
    params = ", ".join("?" * len(serialized))

    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            f"INSERT INTO karakterek ({cols}) VALUES ({params})",
            list(serialized.values()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def load_karakter(karakter_id: int, db_path: Path = DB_PATH) -> dict:
    """Load a character by id, deserialising JSON columns."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM karakterek WHERE id = ?", (karakter_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise ValueError(f"Nem található karakter: id={karakter_id}")

    result = dict(row)
    for col in _JSON_COLS:
        if result.get(col):
            result[col] = json.loads(result[col])
    return result


def save_from_npc_result(npc_result: dict, db_path: Path = DB_PATH) -> int:
    """
    Persist an NPC result returned by npc_generator.generate_npc().

    npc_result shape:
        {"concept": {...}, "stat_block": {...}, "character": {...}}

    Returns:
        The new row id.
    """
    concept = npc_result.get("concept") or {}
    sb      = npc_result.get("stat_block") or {}
    char    = npc_result.get("character") or {}
    combat  = sb.get("combat") or {}

    row: dict = {
        "kaszt":     sb.get("class", ""),
        "szint":     sb.get("level", 1),
        "njk_tipus": concept.get("importance", "minor"),
        "faj":       sb.get("race"),
        "szerep":    concept.get("role"),
        "tulajdonsagok": sb.get("stats") or {},
        "harci_ertekek": {
            "ke":          combat.get("ke", 0),
            "te":          combat.get("te", 0),
            "ve":          combat.get("ve", 0),
            "ce":          combat.get("ce") or 0,
            "ep":          combat.get("ep", 0),
            "fp":          combat.get("fp"),
            "fp_formula":  combat.get("fp_formula"),
            "kp":          combat.get("kp"),
            "kp_per_szint": combat.get("kp_per_szint"),
        },
        "nev":       char.get("name"),
        "nem":       char.get("gender"),
        "kor_leiras":  char.get("age_description"),
        "megjelenes":  char.get("appearance"),
        "szemelyiseg": char.get("personality"),
        "elotortenete": char.get("background"),
        "szolasmod":   char.get("speech_style"),
        "motivacio":   char.get("motivation"),
        "titok":       char.get("secret"),
        "idegenekhez_viszonyulas": char.get("attitude_to_strangers"),
    }

    serialized = {
        k: json.dumps(v, ensure_ascii=False) if k in _JSON_COLS else v
        for k, v in row.items()
        if v is not None
    }

    cols   = ", ".join(serialized.keys())
    params = ", ".join("?" * len(serialized))

    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            f"INSERT INTO karakterek ({cols}) VALUES ({params})",
            list(serialized.values()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def row_to_npc(row: dict) -> dict:
    """
    Convert a loaded karakterek row to the NPC result shape the frontend expects.
    This matches the shape returned by npc_generator.generate_npc().
    """
    harci = row.get("harci_ertekek") or {}
    return {
        "id":         row["id"],
        "letrehozva": row.get("letrehozva"),
        "character": {
            "name":                  row.get("nev"),
            "gender":                row.get("nem"),
            "age_description":       row.get("kor_leiras"),
            "appearance":            row.get("megjelenes"),
            "personality":           row.get("szemelyiseg"),
            "background":            row.get("elotortenete"),
            "speech_style":          row.get("szolasmod"),
            "motivation":            row.get("motivacio"),
            "secret":                row.get("titok"),
            "attitude_to_strangers": row.get("idegenekhez_viszonyulas"),
        },
        "stat_block": {
            "race":         row.get("faj"),
            "class":        row["kaszt"],
            "level":        row["szint"],
            "total_points": None,
            "stats":        row.get("tulajdonsagok") or {},
            "combat":       harci,
        },
        "concept": {
            "importance": row["njk_tipus"],
            "role":       row.get("szerep"),
        },
    }


def list_karakterek(db_path: Path = DB_PATH) -> list[dict]:
    """Return all characters as NPC-shaped dicts, newest first."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, kaszt, szint, njk_tipus, faj, szerep,
                   nev, harci_ertekek, letrehozva
            FROM karakterek
            ORDER BY id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    result = []
    for r in rows:
        d = dict(r)
        if d.get("harci_ertekek"):
            d["harci_ertekek"] = json.loads(d["harci_ertekek"])
        harci = d.get("harci_ertekek") or {}
        result.append({
            "id":         d["id"],
            "letrehozva": d["letrehozva"],
            "character":  {"name": d.get("nev")},
            "stat_block": {
                "race":   d.get("faj"),
                "class":  d["kaszt"],
                "level":  d["szint"],
                "combat": harci,
            },
            "concept": {
                "importance": d["njk_tipus"],
                "role":       d.get("szerep"),
            },
        })
    return result


def get_kepzettsegek(kaszt_nev: str, szint: int, db_path: Path = DB_PATH) -> list[dict]:
    """Return skills granted to a class up to the given level, ordered by szint_tol then name."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT ke.nev, ke.tipus, ke.kategoria,
                   kk.fok, kk.szazalek, kk.szint_tol,
                   ke.ar_alapfok, ke.ar_mesterfok
            FROM kaszt_kepzettsegek kk
            JOIN kepzettsegek ke ON ke.id = kk.kepzettseg_id
            JOIN kasztok ka    ON ka.id = kk.kaszt_id
            WHERE ka.nev = ? AND kk.szint_tol <= ?
            ORDER BY kk.szint_tol, ke.nev
            """,
            (kaszt_nev, szint),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_karakter(karakter_id: int, db_path: Path = DB_PATH) -> bool:
    """Delete a character by id. Returns True if a row was deleted."""
    conn = get_connection(db_path)
    try:
        cur = conn.execute("DELETE FROM karakterek WHERE id = ?", (karakter_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def update_karakter(
    karakter_id: int,
    db_path: Path = DB_PATH,
    **fields,
) -> None:
    """
    Patch any columns of an existing character.

    JSON columns (felszereles, celok) can be passed as Python lists/dicts —
    they are serialised automatically.

    Example:
        update_karakter(3, nev="Aldric Vörös", celok=["Bosszú", "Gazdagság"])
    """
    serialized = {
        k: json.dumps(v, ensure_ascii=False) if k in _JSON_COLS and not isinstance(v, str) else v
        for k, v in fields.items()
    }
    if not serialized:
        return

    set_clause = ", ".join(f"{k} = ?" for k in serialized)
    set_clause += ", frissitve = datetime('now')"

    conn = get_connection(db_path)
    try:
        conn.execute(
            f"UPDATE karakterek SET {set_clause} WHERE id = ?",
            [*serialized.values(), karakter_id],
        )
        conn.commit()
    finally:
        conn.close()
