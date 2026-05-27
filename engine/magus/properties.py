"""
MAGUS NPC property generation and adjustment.

Rolls all 10 properties using class-specific dice formulas (DB lookup),
then adjusts upward to meet the NPC type minimum total threshold.
"""
from __future__ import annotations

import random
import sqlite3
from pathlib import Path

from engine.magus.db import DB_PATH, get_connection
from engine.magus.dice import DEFAULT_FORMULA, roll_formula

# Canonical property names — must match kaszt_tulajdonsag_dobas.tulajdonsag
TULAJDONSAGOK: list[str] = [
    "ero", "ugyesseg", "gyorsasag", "allokepesseg",
    "egeszseg", "szepseg", "asztral", "akarateroe",
    "intelligencia", "erzekeles",
]

TULAJDONSAG_NEVEK: dict[str, str] = {
    "ero":           "Erő",
    "ugyesseg":      "Ügyesség",
    "gyorsasag":     "Gyorsaság",
    "allokepesseg":  "Állóképesség",
    "egeszseg":      "Egészség",
    "szepseg":       "Szépség",
    "asztral":       "Asztrál",
    "akarateroe":     "Akaraterő",
    "intelligencia": "Intelligencia",
    "erzekeles":     "Érzékelés",
}


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _load_class_formulas(kaszt_nev: str, conn: sqlite3.Connection) -> dict[str, dict]:
    rows = conn.execute(
        """
        SELECT ktd.tulajdonsag,
               df.formula, df.dice_count, df.dice_sides,
               df.modifier, df.advantage, df.avg, df.max_val
        FROM kaszt_tulajdonsag_dobas ktd
        JOIN kasztok k  ON k.id  = ktd.kaszt_id
        JOIN dice_formulas df ON df.id = ktd.formula_id
        WHERE k.nev = ?
        """,
        (kaszt_nev,),
    ).fetchall()
    return {r["tulajdonsag"]: dict(r) for r in rows}


def _load_spec_training(kaszt_nev: str, conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT ksk.tulajdonsag, ksk.max_bonus
        FROM kaszt_spec_kepzetes ksk
        JOIN kasztok k ON k.id = ksk.kaszt_id
        WHERE k.nev = ?
        """,
        (kaszt_nev,),
    ).fetchall()
    return {r["tulajdonsag"]: r["max_bonus"] for r in rows}


def _get_min_total(njk_tipus: str, conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT ertek FROM codes WHERE code_type='njk_tipus_min_pont' AND code_no=?",
        (njk_tipus,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Ismeretlen NJK típus: {njk_tipus!r}")
    return row["ertek"]


# ---------------------------------------------------------------------------
# Adjustment algorithm
# ---------------------------------------------------------------------------

def _adjust_properties(
    props: dict[str, int],
    avgs: dict[str, float],
    min_total: int,
    max_vals: dict[str, int],
) -> tuple[dict[str, int], int, list[dict]]:
    """
    Increment properties until sum >= min_total.

    Each cycle:
      1. Increment next property in avg-descending order (random tie-break)
      2. Increment property most below its avg (random tie-break)

    Returns (adjusted_props, steps_taken, log).
    """
    sorted_props = sorted(
        TULAJDONSAGOK,
        key=lambda p: (avgs[p], random.random()),
        reverse=True,
    )

    steps = 0
    log: list[dict] = []

    while sum(props.values()) < min_total:
        made_progress = False
        for prop in sorted_props:
            if sum(props.values()) >= min_total:
                break

            if props[prop] < max_vals[prop]:
                old = props[prop]
                props[prop] += 1
                steps += 1
                made_progress = True
                log.append({"ok": "avg_rank", "prop": prop,
                             "elotte": old, "utan": props[prop],
                             "ossz": sum(props.values())})

            if sum(props.values()) >= min_total:
                break

            candidates = [(p, avgs[p] - props[p])
                          for p in TULAJDONSAGOK if props[p] < max_vals[p]]
            if candidates:
                max_deficit = max(d for _, d in candidates)
                chosen = random.choice([p for p, d in candidates if d == max_deficit])
                old = props[chosen]
                props[chosen] += 1
                steps += 1
                made_progress = True
                log.append({"ok": "avg_deficit", "prop": chosen,
                             "elotte": old, "utan": props[chosen],
                             "ossz": sum(props.values())})

        if not made_progress:
            break

    return props, steps, log


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_npc_properties(
    kaszt_nev: str,
    njk_tipus: str = "atlagos",
    db_path: Path = DB_PATH,
) -> dict:
    """
    Roll and adjust NPC properties for the given class and NPC type.

    Returns: kaszt, njk_tipus, tulajdonsagok, rolled_props, ossz_pont,
             rolled_total, min_pont, adjusted, adj_steps, adj_log,
             avgs, formula_names, max_vals
    """
    conn = get_connection(db_path)
    try:
        formulas      = _load_class_formulas(kaszt_nev, conn)
        spec_training = _load_spec_training(kaszt_nev, conn)
        min_total     = _get_min_total(njk_tipus, conn)
    finally:
        conn.close()

    avgs     = {p: formulas.get(p, DEFAULT_FORMULA)["avg"]     for p in TULAJDONSAGOK}
    max_vals = {
        p: formulas.get(p, DEFAULT_FORMULA)["max_val"] + spec_training.get(p, 0)
        for p in TULAJDONSAGOK
    }

    rolled_props = {p: roll_formula(formulas.get(p, DEFAULT_FORMULA)) for p in TULAJDONSAGOK}
    rolled_total = sum(rolled_props.values())

    props     = dict(rolled_props)
    adj_steps = 0
    adj_log: list[dict] = []
    if rolled_total < min_total:
        props, adj_steps, adj_log = _adjust_properties(props, avgs, min_total, max_vals)

    return {
        "kaszt":         kaszt_nev,
        "njk_tipus":     njk_tipus,
        "tulajdonsagok": props,
        "rolled_props":  rolled_props,
        "ossz_pont":     sum(props.values()),
        "rolled_total":  rolled_total,
        "min_pont":      min_total,
        "adjusted":      rolled_total < min_total,
        "adj_steps":     adj_steps,
        "adj_log":       adj_log,
        "avgs":          avgs,
        "formula_names": {p: formulas.get(p, DEFAULT_FORMULA)["formula"] for p in TULAJDONSAGOK},
        "max_vals":      max_vals,
    }
