"""
Genesys narrative-dice combat engine.

Uses the generic Ruleset.get() interface to read all game data — no
Genesys-specific method names appear on the Ruleset ABC.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Optional

from rules.loader import Ruleset, get_default

# ---------------------------------------------------------------------------
# Dice resolution model
#
# The six Genesys outcome symbols and their cancellation pairs are the core
# contract of this engine. Rulesets express dice faces using these names.
# ---------------------------------------------------------------------------

_SYMBOL_TO_FIELD: dict[str, str] = {
    "success":   "successes",
    "failure":   "failures",
    "advantage": "advantages",
    "threat":    "threats",
    "triumph":   "triumphs",
    "despair":   "despairs",
}


@dataclass
class RollResult:
    successes: int = 0
    failures: int = 0
    advantages: int = 0
    threats: int = 0
    triumphs: int = 0
    despairs: int = 0

    @property
    def net_successes(self) -> int:
        return (self.successes + self.triumphs) - (self.failures + self.despairs)

    @property
    def net_advantages(self) -> int:
        return self.advantages - self.threats

    @property
    def is_success(self) -> bool:
        return self.net_successes > 0

    def describe(self, symbols: dict[str, str]) -> str:
        parts = []
        if self.net_successes > 0:
            parts.append(f"{self.net_successes}{symbols['success']}")
        elif self.net_successes < 0:
            parts.append(f"{abs(self.net_successes)}{symbols['failure']}")
        if self.net_advantages > 0:
            parts.append(f"{self.net_advantages}{symbols['advantage']}")
        elif self.net_advantages < 0:
            parts.append(f"{abs(self.net_advantages)}{symbols['threat']}")
        if self.triumphs:
            parts.append(f"{self.triumphs}{symbols['triumph']}")
        if self.despairs:
            parts.append(f"{self.despairs}{symbols['despair']}")
        return " ".join(parts) if parts else "No result"

    def __str__(self) -> str:
        return (
            f"{self.net_successes:+d}suc {self.net_advantages:+d}adv"
            + (f" {self.triumphs}tri" if self.triumphs else "")
            + (f" {self.despairs}des" if self.despairs else "")
        ).strip()


# ---------------------------------------------------------------------------
# Dice pool rolling
# ---------------------------------------------------------------------------

def roll_dice_pool(pool: dict[str, int], ruleset: Ruleset) -> RollResult:
    """Roll {die_type: count} pool; die definitions loaded from ruleset."""
    dice_defs: dict = ruleset.get("dice")
    result = RollResult()

    for die_type, count in pool.items():
        if die_type not in dice_defs:
            raise KeyError(
                f"Die type '{die_type}' not in ruleset '{ruleset.name}'. "
                f"Available: {list(dice_defs)}"
            )
        faces: list[list[str]] = dice_defs[die_type]["faces"]
        for _ in range(count):
            for symbol in random.choice(faces):
                if symbol != "blank":
                    attr = _SYMBOL_TO_FIELD.get(symbol)
                    if attr is None:
                        raise KeyError(f"Unknown symbol '{symbol}' in ruleset '{ruleset.name}'")
                    setattr(result, attr, getattr(result, attr) + 1)

    return result


# ---------------------------------------------------------------------------
# Initiative pool-building strategies
# ---------------------------------------------------------------------------

def _pool_characteristic_skill(
    characteristic: int,
    skill_rank: int,
    initiative_cfg: dict,
) -> dict[str, int]:
    base_die     = initiative_cfg["positive_die"]
    upgraded_die = initiative_cfg["upgrade_die"]
    proficiency  = min(characteristic, skill_rank)
    ability      = max(characteristic, skill_rank) - proficiency
    pool: dict[str, int] = {}
    if ability:
        pool[base_die] = ability
    if proficiency:
        pool[upgraded_die] = proficiency
    return pool


_POOL_BUILDERS: dict[str, Callable[[int, int, dict], dict[str, int]]] = {
    "characteristic_skill": _pool_characteristic_skill,
}


def _build_initiative_pool(
    characteristic: int,
    skill_rank: int,
    ruleset: Ruleset,
) -> dict[str, int]:
    initiative_cfg = ruleset.get("initiative")
    strategy       = initiative_cfg["pool_building"]
    builder        = _POOL_BUILDERS.get(strategy)
    if builder is None:
        raise KeyError(
            f"Unknown pool-building strategy '{strategy}' in ruleset "
            f"'{ruleset.name}'. Known: {list(_POOL_BUILDERS)}"
        )
    return builder(characteristic, skill_rank, initiative_cfg)


# ---------------------------------------------------------------------------
# Initiative
# ---------------------------------------------------------------------------

@dataclass
class InitiativeSlot:
    side: str
    successes: int
    advantages: int
    roll: RollResult
    actor: Optional[str] = None

    def sort_key(self) -> tuple[int, int]:
        return (self.successes, self.advantages)


def roll_initiative(
    name: str,
    side: str,
    characteristic: int,
    skill_rank: int,
    skill_name: str,
    ruleset: Ruleset,
) -> InitiativeSlot:
    pool    = _build_initiative_pool(characteristic, skill_rank, ruleset)
    roll    = roll_dice_pool(pool, ruleset)
    symbols = ruleset.get("dice_symbols")
    print(
        f"  [{side}] {name} rolls {skill_name}: "
        f"{roll.describe(symbols)} -> "
        f"{roll.net_successes} successes, {roll.net_advantages} advantages"
    )
    return InitiativeSlot(
        side=side,
        successes=roll.net_successes,
        advantages=roll.net_advantages,
        roll=roll,
        actor=name,
    )


def build_initiative_order(slots: list[InitiativeSlot]) -> list[InitiativeSlot]:
    return sorted(slots, key=lambda s: s.sort_key(), reverse=True)


# ---------------------------------------------------------------------------
# Combatant  (pure state)
# ---------------------------------------------------------------------------

@dataclass
class Combatant:
    name: str
    side: str
    wound_threshold: int
    strain_threshold: int
    soak: int
    wounds_current: int = 0
    strain_current: int = 0
    critical_injuries: list[str] = field(default_factory=list)

    @property
    def is_incapacitated(self) -> bool:
        return self.wounds_current >= self.wound_threshold

    @property
    def is_unconscious(self) -> bool:
        return self.strain_current >= self.strain_threshold

    @property
    def is_active(self) -> bool:
        return not self.is_incapacitated and not self.is_unconscious

    def apply_damage(self, raw_damage: int) -> int:
        wounds_taken = max(0, raw_damage - self.soak)
        self.wounds_current += wounds_taken
        return wounds_taken

    def apply_strain(self, amount: int) -> None:
        self.strain_current += amount

    def status_line(self) -> str:
        flags = ""
        if self.is_incapacitated:
            flags += " [INCAPACITATED]"
        if self.is_unconscious:
            flags += " [UNCONSCIOUS]"
        return (
            f"{self.name} | wounds {self.wounds_current}/{self.wound_threshold} "
            f"| strain {self.strain_current}/{self.strain_threshold}{flags}"
        )


# ---------------------------------------------------------------------------
# TurnState
# ---------------------------------------------------------------------------

class TurnState:
    def __init__(self, ruleset: Ruleset) -> None:
        limits = ruleset.get("turn_actions", "maneuvers", "limit")
        self._free_maneuvers: int    = limits["free_per_turn"]
        self._extra_maneuvers: int   = limits["additional"]["count"]
        self._extra_strain_cost: int = limits["additional"]["cost"]["strain"]
        self._max_maneuvers: int     = self._free_maneuvers + self._extra_maneuvers
        self._action_trade: bool     = ruleset.get(
            "turn_actions", "actions", "trade_action_for_maneuver"
        ).get("allowed", False)

        self.maneuvers_used: int = 0
        self.action_used: bool   = False

    def use_maneuver(self, combatant: Combatant) -> bool:
        if self.maneuvers_used >= self._max_maneuvers:
            print(f"  {combatant.name} has no maneuvers left this turn.")
            return False
        if self.maneuvers_used >= self._free_maneuvers:
            combatant.apply_strain(self._extra_strain_cost)
            print(
                f"  {combatant.name} takes {self._extra_strain_cost} strain "
                f"for a second maneuver."
            )
        self.maneuvers_used += 1
        return True

    def use_action(self, combatant: Combatant) -> bool:
        if self.action_used:
            print(f"  {combatant.name} has already used their action this turn.")
            return False
        self.action_used = True
        return True

    def trade_action_for_maneuver(self, combatant: Combatant) -> bool:
        if not self._action_trade:
            print("  Ruleset does not allow trading actions for maneuvers.")
            return False
        if self.action_used:
            print(f"  {combatant.name} already used their action; cannot trade.")
            return False
        self.action_used = True
        return self.use_maneuver(combatant)


# ---------------------------------------------------------------------------
# Round management
# ---------------------------------------------------------------------------

@dataclass
class CombatRound:
    number: int
    order: list[InitiativeSlot]
    _index: int = field(default=0, init=False)

    @property
    def current_slot(self) -> Optional[InitiativeSlot]:
        return self.order[self._index] if self._index < len(self.order) else None

    def advance(self) -> None:
        self._index += 1

    @property
    def is_complete(self) -> bool:
        return self._index >= len(self.order)


class CombatEncounter:
    """Manages a full Genesys combat encounter."""

    def __init__(
        self,
        name: str = "Combat Encounter",
        ruleset: Optional[Ruleset] = None,
    ) -> None:
        self.name          = name
        self.ruleset       = ruleset if ruleset is not None else get_default()
        self.round_number  = 0
        self.slots:        list[InitiativeSlot]   = []
        self.combatants:   dict[str, Combatant]   = {}
        self.current_round: Optional[CombatRound] = None

    def add_combatant(
        self,
        combatant: Combatant,
        characteristic: int,
        skill_rank: int,
        skill_name: Optional[str] = None,
    ) -> None:
        resolved_skill = skill_name or self.ruleset.get("initiative", "default_skill")
        self.combatants[combatant.name] = combatant
        slot = roll_initiative(
            name=combatant.name,
            side=combatant.side,
            characteristic=characteristic,
            skill_rank=skill_rank,
            skill_name=resolved_skill,
            ruleset=self.ruleset,
        )
        self.slots.append(slot)

    def start(self) -> None:
        self.slots  = build_initiative_order(self.slots)
        symbols     = self.ruleset.get("dice_symbols")
        suc_sym     = symbols["success"]
        adv_sym     = symbols["advantage"]

        print(f"\n=== {self.name} -- Initiative Order ===")
        for i, slot in enumerate(self.slots, 1):
            print(
                f"  {i}. [{slot.side}] {slot.actor}  "
                f"({slot.successes}{suc_sym} {slot.advantages}{adv_sym})"
            )
        self._begin_round()

    def _begin_round(self) -> None:
        self.round_number += 1
        self.current_round = CombatRound(number=self.round_number, order=self.slots)
        print(f"\n{'='*40}\n  ROUND {self.round_number}\n{'='*40}")

    def next_turn(self) -> Optional[tuple[InitiativeSlot, Combatant, TurnState]]:
        if self.current_round is None:
            return None

        while not self.current_round.is_complete:
            slot      = self.current_round.current_slot
            combatant = self.combatants.get(slot.actor) if slot else None
            self.current_round.advance()

            if combatant is None or not combatant.is_active:
                label = "incapacitated/unconscious" if combatant else "unassigned"
                print(f"  -> Skipping ({label}): {slot.actor if slot else '?'}")
                continue

            print(f"\n--- {slot.actor}'s turn [{slot.side}] ---")
            return slot, combatant, TurnState(self.ruleset)

        if self._one_side_defeated():
            print("\n=== Combat Over ===")
            self._print_status()
            return None

        self._print_status()
        self._begin_round()
        return self.next_turn()

    def apply_damage(self, target_name: str, raw_damage: int) -> None:
        combatant    = self.combatants[target_name]
        wounds_taken = combatant.apply_damage(raw_damage)
        dr           = self.ruleset.get("damage_and_resilience")
        print(
            f"  {target_name} takes {wounds_taken} wounds "
            f"(soak {combatant.soak} absorbed {raw_damage - wounds_taken})."
        )
        if combatant.is_incapacitated:
            print(f"  {target_name} INCAPACITATED. {dr['wound_threshold']['exceed_effect']}")

    def apply_strain(self, target_name: str, amount: int) -> None:
        combatant = self.combatants[target_name]
        combatant.apply_strain(amount)
        dr = self.ruleset.get("damage_and_resilience")
        print(f"  {target_name} takes {amount} strain.")
        if combatant.is_unconscious:
            print(f"  {target_name} UNCONSCIOUS. {dr['strain_threshold']['exceed_effect']}")

    def _one_side_defeated(self) -> bool:
        sides: dict[str, list[bool]] = {}
        for c in self.combatants.values():
            sides.setdefault(c.side, []).append(c.is_active)
        return any(not any(active) for active in sides.values())

    def _print_status(self) -> None:
        print("\n  -- Status --")
        for c in self.combatants.values():
            print(f"  {c.status_line()}")
