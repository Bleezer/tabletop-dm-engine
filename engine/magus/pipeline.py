"""
MAGUS DM pipeline — main entry point.

Usage:
    python -m engine.magus.pipeline "Torozon Tavernája"
    python -m engine.magus.pipeline "Bagor Kalandozók Boltja" --output result.json
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import anthropic

from engine.magus.location_generator import generate_location

ROOT = Path(__file__).parent.parent.parent

_RACES_FILE   = ROOT / "world" / "magus" / "magus_races.json"
_CLASSES_FILE = ROOT / "world" / "magus" / "classes.json"


def _load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _print_result(result: dict) -> None:
    desc  = result["description"]
    npcs  = result["npcs"]
    found = result["location_data"] is not None

    print(f"\n{'='*60}")
    print(f"  {result['name'].upper()}")
    if found:
        ld = result["location_data"]
        print(f"  {ld.get('negyed','')} — {ld.get('tipus','')}")
    print(f"{'='*60}\n")

    print(desc.get("sensory_description", ""))
    print()
    print(f"Hangulat: {desc.get('atmosphere', '')}")
    print()

    layout = desc.get("layout", [])
    if layout:
        print("Területek:")
        for area in layout:
            print(f"  • {area}")
        print()

    print(f"Jelenet: {desc.get('current_scene', '')}")
    print()

    details = desc.get("notable_details", [])
    if details:
        print("Részletek:")
        for d in details:
            print(f"  → {d}")
        print()

    dm = desc.get("dm_notes")
    if dm:
        print(f"[Mesélőnek] {dm}\n")

    print(f"{'─'*60}")
    print(f"NPC-K ({len(npcs)} db)")
    print(f"{'─'*60}")

    for i, npc in enumerate(npcs, 1):
        if "error" in npc:
            print(f"\n{i}. [Hiba: {npc['error']}]")
            continue

        char = npc.get("character", {})
        conc = npc.get("concept", {})
        sb   = npc.get("stat_block", {})
        spec = npc.get("spec", {})

        gender  = char.get("gender", "?")
        age     = char.get("age_description", "")
        name    = char.get("name", "Névtelen")
        race_c  = sb.get("race", conc.get("race", "?"))
        class_c = sb.get("class", conc.get("class_name", "?"))
        level   = sb.get("level", conc.get("level", "?"))
        role    = conc.get("role", spec.get("role", "?"))
        import_ = conc.get("importance", spec.get("importance", "?"))

        print(f"\n{i}. {name}  [{race_c} {class_c} {level}. szint]  ({import_})")
        print(f"   Szerep: {role}  |  {gender}, {age}")
        print(f"   Megjelenés: {char.get('appearance', '')}")
        print(f"   Személyiség: {char.get('personality', '')}")
        print(f"   Háttér: {char.get('background', '')}")
        print(f"   Beszédstílus: {char.get('speech_style', '')}")
        print(f"   Motiváció: {char.get('motivation', '')}")
        if char.get("secret"):
            print(f"   [Titok] {char['secret']}")
        print(f"   Idegenek felé: {char.get('attitude_to_strangers', '?')}")

        c = sb.get("combat", {})
        s = sb.get("stats", {})
        print(
            f"   ÉP {c.get('ep','?')} | "
            f"KÉ {c.get('ke','?')} TÉ {c.get('te','?')} VÉ {c.get('ve','?')}"
        )
        if s:
            stat_line = "  ".join(
                f"{k[:3]}:{v}" for k, v in list(s.items())[:5]
            )
            print(f"   Stat: {stat_line}…")

    print()


def generate(location_name: str) -> dict:
    """
    Full pipeline: load world data → generate location → generate NPCs.
    Returns the complete result dict.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable is not set")

    races_data   = _load_json(_RACES_FILE)
    classes_data = _load_json(_CLASSES_FILE)
    client       = anthropic.Anthropic(api_key=api_key)

    return generate_location(
        location_name = location_name,
        races_data    = races_data,
        classes_data  = classes_data,
        client        = client,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="MAGUS DM location + NPC generator")
    parser.add_argument("location", help="Helyszín neve (pl. 'Torozon Tavernája')")
    parser.add_argument("--output", "-o", help="JSON output fájl (opcionális)")
    parser.add_argument("--json-only", action="store_true", help="Csak JSON kimenet")
    args = parser.parse_args()

    result = generate(args.location)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Mentve: {out_path}")

    if args.json_only:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_result(result)


if __name__ == "__main__":
    main()
