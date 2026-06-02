"""
Legacy stat helpers used by the Claude API NPC pipeline (npc_generator.py).

build_stat_block / format_stat_block work with raw JSON data (races_data,
classes_data) rather than the SQLite DB — they exist to inject a compact
stat summary into the AI prompt during NPC generation.
"""
from __future__ import annotations

import random

_STAT_NAMES = [
    "ero", "allokepesseg", "gyorsasag", "ugyesseg",
    "egeszseg", "szepseg", "intelligencia", "akarateroe", "asztral",
]

_STAT_LABELS = {
    "ero": "Erő", "allokepesseg": "Állóképesség", "gyorsasag": "Gyorsaság",
    "ugyesseg": "Ügyesség", "egeszseg": "Egészség", "szepseg": "Szépség",
    "intelligencia": "Intelligencia", "akarateroe": "Akaratero", "asztral": "Asztrál",
}


def _find_race(name: str, races_data: dict) -> dict | None:
    target = name.strip().lower()
    for race in races_data["races"]:
        if race["name"].lower() == target:
            return race
    for race in races_data["races"]:
        if target in race["name"].lower() or race["name"].lower() in target:
            return race
    return None


def _find_class(name: str, classes_data: dict) -> dict | None:
    target = name.strip().lower()
    for cls in classes_data["kasztok"]:
        if cls["nev"].lower() == target:
            return cls
    for cls in classes_data["kasztok"]:
        if target in cls["nev"].lower() or cls["nev"].lower() in target:
            return cls
    return None


def _distribute_stats(total_points: int, race: dict | None) -> dict[str, int]:
    mods: dict[str, int] = {}
    maxes: dict[str, int] = {}
    if race:
        mods = race.get("stat_modifiers", {})
        for stat, data in race.get("max_stats", {}).items():
            maxes[stat] = data.get("base", 18) if isinstance(data, dict) else 18

    stats = {s: 10 for s in _STAT_NAMES}
    remaining = total_points - sum(stats.values())

    attempts = 0
    while remaining > 0 and attempts < 10_000:
        stat = random.choice(_STAT_NAMES)
        cap = maxes.get(stat, 18) - 1
        if stats[stat] < cap:
            stats[stat] += 1
            remaining -= 1
        attempts += 1

    for stat, mod in mods.items():
        if stat in stats:
            stats[stat] = max(6, min(stats[stat] + mod, maxes.get(stat, 18)))

    return stats


def _derive_combat(stats: dict, cls: dict | None, level: int) -> dict:
    if not cls:
        return {"ep": 10 + level * 4, "ke": 5 + (level - 1) * 2,
                "te": 15 + (level - 1) * 3, "ve": 60 + (level - 1) * 3,
                "ce": None, "hm": 0, "level": level}

    harci   = cls.get("harcertekek", {})
    ep_data = cls.get("ep", {})
    ero_bonus = max(0, stats.get("ero", 10) - 10) // 2

    return {
        "ep":    ep_data.get("alap", 8) + (level - 1) * ep_data.get("szintenként", 4),
        "ke":    harci.get("ke", 5)  + (level - 1) * 2,
        "te":    harci.get("te", 15) + (level - 1) * 3 + ero_bonus,
        "ve":    harci.get("ve", 60) + (level - 1) * 3,
        "ce":    harci.get("ce", 0) or None,
        "hm":    harci.get("hm", 0),
        "level": level,
    }


def build_stat_block(
    race_name: str,
    class_name: str,
    level: int,
    total_points: int,
    races_data: dict,
    classes_data: dict,
) -> dict:
    race   = _find_race(race_name, races_data)
    cls    = _find_class(class_name, classes_data)
    stats  = _distribute_stats(total_points, race)
    combat = _derive_combat(stats, cls, level)
    return {
        "race": race["name"] if race else race_name,
        "class": cls["nev"] if cls else class_name,
        "level": level,
        "total_points": total_points,
        "stats": stats,
        "combat": combat,
    }


def format_stat_block(block: dict) -> str:
    s = block["stats"]
    c = block["combat"]
    rows = "\n".join(f"  {_STAT_LABELS[k]}: {s[k]}" for k in _STAT_NAMES)
    combat_parts = [f"KÉ {c['ke']}  TÉ {c['te']}  VÉ {c['ve']}  ÉP {c['ep']}"]
    if c.get("ce"):
        combat_parts.append(f"CÉ {c['ce']}")
    if c.get("hm"):
        combat_parts.append(f"HM {c['hm']}")
    return (
        f"Faj: {block['race']}  Kaszt: {block['class']}  Szint: {block['level']}\n"
        f"Összpont: {block['total_points']}\n"
        f"Tulajdonságok:\n{rows}\n"
        f"Harci értékek: {' | '.join(combat_parts)}"
    )
