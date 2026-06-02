"""
MAGUS combat stat calculation.

Takes rolled/adjusted properties + class DB data and computes
KÉ, TÉ, VÉ, CÉ, KP, ÉP, FP and applies the free HM distribution strategy.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from engine.magus.core.db import DB_PATH, get_connection
from engine.magus.core.dice import roll_formula
from engine.magus.core.logger import log_stat_calc


# ---------------------------------------------------------------------------
# HM distribution strategies
# ---------------------------------------------------------------------------

def _hm_distribute(te: int, ve: int, ce: int, total: int, mod: int) -> tuple[int, int, int]:
    """
    Distribute `total` free HM points. Returns (added_te, added_ve, added_ce).

    1 — TÉ/VÉ balance: keep VÉ-TÉ = 45; if gap == 45 put on TÉ.
    2 — all on CÉ.
    3 — all on VÉ.
    4 — all on TÉ.
    """
    if mod == 2:
        return 0, 0, total
    if mod == 3:
        return 0, total, 0
    if mod == 4:
        return total, 0, 0

    add_te, add_ve = 0, 0
    for _ in range(total):
        gap = (ve + add_ve) - (te + add_te)
        if gap > 45:
            add_te += 1
        elif gap < 45:
            add_ve += 1
        else:
            add_te += 1  # gap == 45 → TÉ
    return add_te, add_ve, 0


# ---------------------------------------------------------------------------
# DB helper
# ---------------------------------------------------------------------------

def _load_class_combat_data(kaszt_nev: str, conn: sqlite3.Connection) -> dict:
    row = conn.execute(
        """
        SELECT alap_ke, alap_te, alap_ve, alap_ce,
               alap_ep, alap_fp, fp_per_szint_formula_id,
               alap_kp, kp_per_szint,
               hm_per_szint, kotelezo_hm_te, kotelezo_hm_ve,
               szazalek_per_szint, hm_elosztasi_mod
        FROM kasztok WHERE nev = ?
        """,
        (kaszt_nev,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Ismeretlen kaszt: {kaszt_nev!r}")
    data = dict(row)

    if data["fp_per_szint_formula_id"]:
        fp_row = conn.execute(
            "SELECT formula, dice_count, dice_sides, modifier, advantage "
            "FROM dice_formulas WHERE id = ?",
            (data["fp_per_szint_formula_id"],),
        ).fetchone()
        data["fp_formula"] = dict(fp_row)
    else:
        data["fp_formula"] = None

    return data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def calculate_combat_stats(
    kaszt_nev: str,
    props: dict[str, int],
    szint: int,
    db_path: Path = DB_PATH,
) -> dict:
    """
    Derive all combat statistics for a character.

    Args:
        kaszt_nev: DB class name (e.g. 'Fejvadasz')
        props:     final property dict from generate_npc_properties
        szint:     character level (minimum 1)
    """
    conn = get_connection(db_path)
    try:
        c = _load_class_combat_data(kaszt_nev, conn)
    finally:
        conn.close()

    def ab(prop: str) -> int:
        return max(0, props[prop] - 10)

    gy = ab("gyorsasag")
    ue = ab("ugyesseg")
    er = ab("ero")
    eg = ab("egeszseg")

    ke_bonus = szint // 2 if kaszt_nev == "Fejvadasz" else 0
    ke = c["alap_ke"] + gy + ue + ke_bonus
    te = c["alap_te"] + er + ue + gy + c["kotelezo_hm_te"] * szint
    ve = c["alap_ve"] + ue + gy + c["kotelezo_hm_ve"] * szint
    ce = c["alap_ce"] + ue

    szabad_hm_per_szint = c["hm_per_szint"] - c["kotelezo_hm_te"] - c["kotelezo_hm_ve"]
    szabad_hm_ossz      = szabad_hm_per_szint * szint

    hm_free_te, hm_free_ve, hm_free_ce = _hm_distribute(
        te, ve, ce, szabad_hm_ossz, c["hm_elosztasi_mod"]
    )
    te += hm_free_te
    ve += hm_free_ve
    ce += hm_free_ce

    int_bonus = max(0, props["intelligencia"] - 10)
    ue_bonus  = max(0, props["ugyesseg"] - 10)
    kp = c["alap_kp"] + int_bonus + ue_bonus + c["kp_per_szint"] * szint
    ep = c["alap_ep"] + eg

    fp      = c["alap_fp"]
    fp_rolls: list[int] = []
    if c["fp_formula"]:
        for _ in range(szint):
            r = roll_formula(c["fp_formula"])
            fp_rolls.append(r)
            fp += r

    result = {
        "kaszt":               kaszt_nev,
        "szint":               szint,
        "ke":                  ke,
        "te":                  te,
        "ve":                  ve,
        "ce":                  ce,
        "szabad_hm_per_szint": szabad_hm_per_szint,
        "szabad_hm_ossz":      szabad_hm_ossz,
        "kp":                  kp,
        "ep":                  ep,
        "fp":                  fp,
        "fp_rolls":            fp_rolls,
        "fp_formula_str":      c["fp_formula"]["formula"] if c["fp_formula"] else "—",
        "alap_ke":             c["alap_ke"],
        "alap_te":             c["alap_te"],
        "alap_ve":             c["alap_ve"],
        "alap_ce":             c["alap_ce"],
        "alap_kp":             c["alap_kp"],
        "kp_int_bonus":        int_bonus,
        "kp_ue_bonus":         ue_bonus,
        "alap_kp_per_szint":   c["kp_per_szint"],
        "szazalek_per_szint":  c["szazalek_per_szint"],
        "szazalek_ossz":       c["szazalek_per_szint"] * szint,
        "kotelezo_hm_te":      c["kotelezo_hm_te"],
        "kotelezo_hm_ve":      c["kotelezo_hm_ve"],
        "hm_elosztasi_mod":    c["hm_elosztasi_mod"],
        "hm_free_te":          hm_free_te,
        "hm_free_ve":          hm_free_ve,
        "hm_free_ce":          hm_free_ce,
    }
    log_stat_calc(
        kaszt=kaszt_nev,
        szint=szint,
        props=props,
        result=result,
        details={
            "gy": gy, "ue": ue, "er": er, "eg": eg,
            "int_bonus": int_bonus,
            "ke_bonus": ke_bonus,
            "alap_ep": c["alap_ep"],
            "alap_fp": c["alap_fp"],
            "hm_per_szint": c["hm_per_szint"],
        },
    )
    return result
