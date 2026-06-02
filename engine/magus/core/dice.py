"""
Dice formula rolling for MAGUS RPG.
"""
from __future__ import annotations

import random

DEFAULT_FORMULA: dict = {
    "formula": "3k6", "dice_count": 3, "dice_sides": 6,
    "modifier": 0, "advantage": 0, "avg": 10.5, "max_val": 18,
}


def _roll_once(dice_count: int, dice_sides: int, modifier: int) -> int:
    return sum(random.randint(1, dice_sides) for _ in range(dice_count)) + modifier


def roll_formula(f: dict) -> int:
    """Roll a dice formula dict. Respects advantage (roll twice, take higher)."""
    r = _roll_once(f["dice_count"], f["dice_sides"], f["modifier"])
    if f.get("advantage"):
        r = max(r, _roll_once(f["dice_count"], f["dice_sides"], f["modifier"]))
    return r
