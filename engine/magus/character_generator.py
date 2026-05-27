"""
MAGUS character generator — public API entry point.

Imports and re-exports from the four focused modules:
  dice        — formula rolling
  properties  — property generation & adjustment
  combat      — combat stat calculation & HM distribution
  formatters  — text output
"""
from __future__ import annotations

from engine.magus.dice       import roll_formula, DEFAULT_FORMULA
from engine.magus.properties import TULAJDONSAGOK, TULAJDONSAG_NEVEK, generate_npc_properties
from engine.magus.combat     import calculate_combat_stats
from engine.magus.formatters import format_result, format_combat_stats
from engine.magus.karakter   import save_karakter, load_karakter, update_karakter

__all__ = [
    "roll_formula",
    "DEFAULT_FORMULA",
    "TULAJDONSAGOK",
    "TULAJDONSAG_NEVEK",
    "generate_npc_properties",
    "calculate_combat_stats",
    "format_result",
    "format_combat_stats",
    "save_karakter",
    "load_karakter",
    "update_karakter",
]


# ---------------------------------------------------------------------------
# Quick test  (python -m engine.magus.character_generator)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io
    import random
    import sys

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    random.seed()
    for i in range(1, 4):
        print(f"{'═' * 60}")
        print(f"  FEJVADÁSZ #{i}  (8. szint, kiemelt NJK)")
        print(f"{'═' * 60}")
        r = generate_npc_properties("Fejvadasz", "kiemelt")
        print(format_result(r, verbose=True))
        print()
        cs = calculate_combat_stats("Fejvadasz", r["tulajdonsagok"], 8)
        print(format_combat_stats(cs, r["tulajdonsagok"]))
        print()
