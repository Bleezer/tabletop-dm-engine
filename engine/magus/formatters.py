"""
Text formatters for MAGUS character sheets.
"""
from __future__ import annotations

from engine.magus.properties import TULAJDONSAGOK, TULAJDONSAG_NEVEK


def format_result(result: dict, verbose: bool = False) -> str:
    props        = result["tulajdonsagok"]
    rolled_props = result.get("rolled_props", props)
    avgs         = result["avgs"]
    formulas     = result["formula_names"]
    max_vals     = result["max_vals"]
    adjusted     = result["adjusted"]

    lines = [
        f"Kaszt: {result['kaszt']}  |  NJK típus: {result['njk_tipus']}",
        f"{'─' * 65}",
    ]
    if adjusted:
        lines.append(f"{'Tulajdonság':<18} {'Dobott':>6} {'+':>4} {'Végső':>6} {'Átlag':>6} {'Max':>5}  Formula")
    else:
        lines.append(f"{'Tulajdonság':<18} {'Érték':>6} {'Átlag':>6} {'Max':>5}  Formula")
    lines.append(f"{'─' * 65}")

    for p in TULAJDONSAGOK:
        nev    = TULAJDONSAG_NEVEK.get(p, p)
        rolled = rolled_props[p]
        final  = props[p]
        gained = final - rolled
        avg    = avgs[p]
        mval   = max_vals[p]
        mark   = " ▲" if (final - avg) > 2 else (" ▼" if (final - avg) < -2 else "")
        if adjusted:
            gain_str = f"+{gained}" if gained else "  -"
            lines.append(f"{nev:<18} {rolled:>6} {gain_str:>4} {final:>6} {avg:>6.1f} {mval:>5}  {formulas[p]}{mark}")
        else:
            lines.append(f"{nev:<18} {final:>6} {avg:>6.1f} {mval:>5}  {formulas[p]}{mark}")

    adj_info = ""
    if adjusted:
        gained_total = result["ossz_pont"] - result["rolled_total"]
        adj_info = f"  ← +{gained_total} pont korrigálva ({result['adj_steps']} lépés)"
    lines += [
        f"{'─' * 65}",
        f"{'Összpontszám':<18} {result['ossz_pont']:>6}   (min: {result['min_pont']}, dobott: {result['rolled_total']}){adj_info}",
    ]

    if verbose and adjusted and result.get("adj_log"):
        ok_labels = {"avg_rank": "avg-rangsor", "avg_deficit": "legtöbb elmaradás"}
        lines.append(f"\n{'─' * 65}")
        lines.append("Korrekció lépései:")
        for i, step in enumerate(result["adj_log"], 1):
            nev = TULAJDONSAG_NEVEK.get(step["prop"], step["prop"])
            ok  = ok_labels.get(step["ok"], step["ok"])
            lines.append(
                f"  {i:>3}. {nev:<18} {step['elotte']:>2} → {step['utan']:>2}"
                f"  [{ok}]  (összeg: {step['ossz']})"
            )

    return "\n".join(lines)


def format_combat_stats(cs: dict, props: dict[str, int]) -> str:
    def ab(prop: str) -> str:
        v = max(0, props[prop] - 10)
        return f"+{v}" if v else " 0"

    lines = [
        f"{'─' * 60}",
        f"Harci értékek  (szint: {cs['szint']})",
        f"{'─' * 60}",
        f"  KÉ: {cs['ke']:>5}  =  alap {cs['alap_ke']} + gy{ab('gyorsasag')} + üg{ab('ugyesseg')}"
        + (f" + szint/2 ({cs['szint']//2})" if cs["kaszt"] == "Fejvadasz" else ""),
        f"  TÉ: {cs['te']:>5}  =  alap {cs['alap_te']} + er{ab('ero')} + üg{ab('ugyesseg')} + gy{ab('gyorsasag')}"
        + (f" + kHM {cs['kotelezo_hm_te']}×{cs['szint']}" if cs["kotelezo_hm_te"] else "")
        + (f" + szHM +{cs['hm_free_te']}" if cs["hm_free_te"] else ""),
        f"  VÉ: {cs['ve']:>5}  =  alap {cs['alap_ve']} + üg{ab('ugyesseg')} + gy{ab('gyorsasag')}"
        + (f" + kHM {cs['kotelezo_hm_ve']}×{cs['szint']}" if cs["kotelezo_hm_ve"] else "")
        + (f" + szHM +{cs['hm_free_ve']}" if cs["hm_free_ve"] else ""),
        f"  CÉ: {cs['ce']:>5}  =  alap {cs['alap_ce']} + üg{ab('ugyesseg')}"
        + (f" + szHM +{cs['hm_free_ce']}" if cs["hm_free_ce"] else ""),
        f"  (VÉ-TÉ = {cs['ve']-cs['te']}  |  HM mód: {cs['hm_elosztasi_mod']})",
        f"{'─' * 60}",
        f"  Szabad HM: {cs['szabad_hm_ossz']:>4}  ({cs['szabad_hm_per_szint']}/szint × {cs['szint']} szint)"
        f"  → TÉ+{cs['hm_free_te']} VÉ+{cs['hm_free_ve']} CÉ+{cs['hm_free_ce']}",
        f"  KP:        {cs['kp']:>4}  (alap {cs['alap_kp']} + int{ab('intelligencia')} + üg{ab('ugyesseg')} + {cs['alap_kp_per_szint']}×{cs['szint']} szerzett)",
        f"  ÉP:        {cs['ep']:>4}  (alap + eg{ab('egeszseg')})",
        f"  FP:        {cs['fp']:>4}  ({cs['fp_formula_str']} × {cs['szint']} szint → {cs['fp_rolls']})",
        f"  Szabad %:  {cs['szazalek_ossz']:>4}  ({cs['szazalek_per_szint']}%/szint × {cs['szint']} szint)",
    ]
    return "\n".join(lines)
