"""
D&D 5e combat engine.

Uses d20 + modifier vs DC/AC, HP/AC health model, and the D&D action economy
(action / bonus action / reaction / movement). Loads flavour text and tables
from a ruleset JSON via the generic Ruleset.get() interface.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from rules.loader import Ruleset, get_default


# ---------------------------------------------------------------------------
# Dice
# ---------------------------------------------------------------------------

@dataclass
class D20Roll:
    natural: int        # raw die result 1-20
    modifier: int
    dc: Optional[int] = None

    @property
    def total(self) -> int:
        return self.natural + self.modifier

    @property
    def is_success(self) -> bool:
        return self.dc is None or self.total >= self.dc

    @property
    def is_critical_success(self) -> bool:
        return self.natural == 20

    @property
    def is_critical_fail(self) -> bool:
        return self.natural == 1

    def __str__(self) -> str:
        dc_part = f" vs DC {self.dc}" if self.dc is not None else ""
        return f"{self.natural}+{self.modifier}={self.total}{dc_part}"


def roll_d20(modifier: int = 0, dc: Optional[int] = None) -> D20Roll:
    return D20Roll(natural=random.randint(1, 20), modifier=modifier, dc=dc)


def roll_damage(dice_str: str, critical: bool = False) -> int:
    """Parse and roll a damage expression like '2d6' or '1d8'.
    On a critical hit, dice are doubled per D&D 5e rules."""
    count_str, sides_str = dice_str.lower().split("d")
    count = int(count_str) * (2 if critical else 1)
    sides = int(sides_str)
    return sum(random.randint(1, sides) for _ in range(count))


# ---------------------------------------------------------------------------
# Combatant
# ---------------------------------------------------------------------------

@dataclass
class DnDCombatant:
    name: str
    side: str
    hp_max: int
    armor_class: int
    speed_ft: int
    hp_current: int = field(init=False)
    conditions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.hp_current = self.hp_max

    @property
    def is_down(self) -> bool:
        return self.hp_current <= 0

    @property
    def is_active(self) -> bool:
        return not self.is_down and "incapacitated" not in self.conditions

    def take_damage(self, amount: int) -> int:
        """Apply damage; returns actual damage dealt."""
        actual = min(amount, self.hp_current)
        self.hp_current -= actual
        return actual

    def heal(self, amount: int) -> int:
        """Restore HP up to max; returns HP actually restored."""
        restored = min(amount, self.hp_max - self.hp_current)
        self.hp_current += restored
        return restored

    def status_line(self) -> str:
        flags = " [DOWN]" if self.is_down else ""
        conds = f" ({', '.join(self.conditions)})" if self.conditions else ""
        return (
            f"{self.name} | HP {self.hp_current}/{self.hp_max} "
            f"| AC {self.armor_class}{flags}{conds}"
        )


# ---------------------------------------------------------------------------
# Action economy
# ---------------------------------------------------------------------------

@dataclass
class TurnBudget:
    """D&D 5e per-turn action resources."""
    speed_ft: int
    action_used: bool = False
    bonus_action_used: bool = False
    reaction_used: bool = False
    movement_used_ft: int = 0

    @property
    def movement_remaining_ft(self) -> int:
        return max(0, self.speed_ft - self.movement_used_ft)

    def use_action(self, actor: str) -> bool:
        if self.action_used:
            print(f"  {actor} already used their action.")
            return False
        self.action_used = True
        return True

    def use_bonus_action(self, actor: str) -> bool:
        if self.bonus_action_used:
            print(f"  {actor} already used their bonus action.")
            return False
        self.bonus_action_used = True
        return True

    def use_reaction(self, actor: str) -> bool:
        if self.reaction_used:
            print(f"  {actor} already used their reaction.")
            return False
        self.reaction_used = True
        return True

    def move(self, ft: int, actor: str) -> int:
        """Move up to ft feet; returns feet actually moved."""
        moved = min(ft, self.movement_remaining_ft)
        self.movement_used_ft += moved
        if moved < ft:
            print(f"  {actor} only has {self.movement_remaining_ft + moved}ft left; moved {moved}ft.")
        return moved


# ---------------------------------------------------------------------------
# Initiative
# ---------------------------------------------------------------------------

@dataclass
class InitiativeEntry:
    actor: str
    side: str
    roll: D20Roll

    @property
    def total(self) -> int:
        return self.roll.total


def roll_initiative(name: str, side: str, dex_modifier: int) -> InitiativeEntry:
    roll = roll_d20(modifier=dex_modifier)
    print(f"  [{side}] {name} initiative: {roll.natural}+{dex_modifier} = {roll.total}")
    return InitiativeEntry(actor=name, side=side, roll=roll)


# ---------------------------------------------------------------------------
# Encounter
# ---------------------------------------------------------------------------

class DnDEncounter:
    """Manages a full D&D 5e combat encounter."""

    def __init__(
        self,
        name: str = "Encounter",
        ruleset: Optional[Ruleset] = None,
    ) -> None:
        self.name         = name
        self.ruleset      = ruleset if ruleset is not None else get_default()
        self.round_number = 0
        self.order:       list[InitiativeEntry]    = []
        self.combatants:  dict[str, DnDCombatant]  = {}
        self._turn_index  = 0

    def add_combatant(
        self,
        combatant: DnDCombatant,
        dex_modifier: int = 0,
    ) -> None:
        self.combatants[combatant.name] = combatant
        entry = roll_initiative(combatant.name, combatant.side, dex_modifier)
        self.order.append(entry)

    def start(self) -> None:
        self.order.sort(key=lambda e: e.total, reverse=True)
        print(f"\n=== {self.name} -- Initiative Order ===")
        for i, entry in enumerate(self.order, 1):
            print(f"  {i}. [{entry.side}] {entry.actor}  (initiative {entry.total})")
        self._begin_round()

    def _begin_round(self) -> None:
        self.round_number += 1
        self._turn_index  = 0
        print(f"\n{'='*40}\n  ROUND {self.round_number}\n{'='*40}")

    def next_turn(self) -> Optional[tuple[InitiativeEntry, DnDCombatant, TurnBudget]]:
        while self._turn_index < len(self.order):
            entry     = self.order[self._turn_index]
            combatant = self.combatants.get(entry.actor)
            self._turn_index += 1

            if combatant is None or not combatant.is_active:
                print(f"  -> Skipping: {entry.actor}")
                continue

            print(f"\n--- {entry.actor}'s turn [{entry.side}] ---")
            return entry, combatant, TurnBudget(speed_ft=combatant.speed_ft)

        if self._one_side_defeated():
            print("\n=== Combat Over ===")
            self._print_status()
            return None

        self._print_status()
        self._begin_round()
        return self.next_turn()

    def attack(
        self,
        attacker_name: str,
        target_name: str,
        attack_bonus: int,
        damage_dice: str,
        damage_bonus: int = 0,
    ) -> None:
        """Resolve a weapon attack roll against a target's AC."""
        target = self.combatants[target_name]
        roll   = roll_d20(modifier=attack_bonus, dc=target.armor_class)

        print(
            f"  {attacker_name} attacks {target_name}: "
            f"{roll.natural}+{attack_bonus}={roll.total} vs AC {target.armor_class}"
        )

        if roll.is_critical_fail:
            print("  Critical miss!")
            return

        if not roll.is_success:
            print("  Miss!")
            return

        dmg    = roll_damage(damage_dice, critical=roll.is_critical_success) + damage_bonus
        actual = target.take_damage(dmg)
        label  = " (CRITICAL HIT)" if roll.is_critical_success else ""
        print(f"  Hit{label}! {target_name} takes {actual} damage. {target.status_line()}")

        if target.is_down:
            print(f"  {target_name} is DOWN!")

    def saving_throw(
        self,
        actor_name: str,
        ability_modifier: int,
        dc: int,
        ability: str = "ability",
    ) -> bool:
        """Roll a saving throw; returns True on success."""
        roll = roll_d20(modifier=ability_modifier, dc=dc)
        outcome = "SUCCESS" if roll.is_success else "FAILURE"
        print(
            f"  {actor_name} {ability} save: {roll.natural}+{ability_modifier}="
            f"{roll.total} vs DC {dc} -> {outcome}"
        )
        return roll.is_success

    def _one_side_defeated(self) -> bool:
        sides: dict[str, list[bool]] = {}
        for c in self.combatants.values():
            sides.setdefault(c.side, []).append(c.is_active)
        return any(not any(active) for active in sides.values())

    def _print_status(self) -> None:
        print("\n  -- Status --")
        for c in self.combatants.values():
            print(f"  {c.status_line()}")
