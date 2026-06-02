"""
MAGUS location generator.

1. Loads existing location data from /world/magus/erion/locations.json (if found)
2. AI generates detailed description, atmosphere, layout and decides which NPCs are present
3. Calls npc_generator for each NPC the AI requests
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anthropic

from engine.magus.agents.npc_generator import generate_npc, _world_system_blocks
from engine.magus.core.logger import get_logger, log_claude_call

logger = get_logger("location_generator")

ROOT  = Path(__file__).parent.parent.parent.parent
MODEL = "claude-sonnet-4-6"

_LOCATIONS_FILE = ROOT / "world" / "magus" / "erion" / "locations.json"


def _load_skill(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


_LOCATION_SKILL = _load_skill(ROOT / "skills" / "location_generator.md")


# ---------------------------------------------------------------------------
# Location data loader
# ---------------------------------------------------------------------------

def _load_location_data(name: str) -> dict | None:
    if not _LOCATIONS_FILE.exists():
        return None
    with open(_LOCATIONS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    import unicodedata

    def _norm(s: str) -> str:
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()

    target = _norm(name.strip())
    for loc in data.get("helyszinek", []):
        loc_name = loc.get("nev", "")
        if _norm(loc_name) == target or target in _norm(loc_name):
            return loc
    return None


def _location_context_str(name: str, data: dict | None) -> str:
    if data is None:
        return f"Helyszín neve: {name}\n(Nincs előzetes adat — teljesen generált helyszín)"
    lines = [
        f"Helyszín: {data.get('nev', name)}",
        f"Negyed: {data.get('negyed', '?')}",
        f"Típus: {data.get('tipus', '?')}",
        f"Leírás: {data.get('leiras', '')}",
    ]
    if data.get('frakcio'):
        lines.append(f"Frakció: {data['frakcio']}")
    if data.get('atmoszfera'):
        lines.append(f"Hangulat: {', '.join(data['atmoszfera'])}")
    existing_npcs = data.get('npck', [])
    if existing_npcs:
        npc_str = '; '.join(
            f"{n.get('nev','?')} ({n.get('szerep','?')})" for n in existing_npcs
        )
        lines.append(f"Ismert NPC-k: {npc_str}")
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Location description tool
# ---------------------------------------------------------------------------

_LOCATION_TOOL: dict[str, Any] = {
    "name": "describe_location",
    "description": (
        "Generáld le a helyszín részletes leírását és döntsd el, "
        "kik tartózkodnak most itt."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sensory_description": {
                "type": "string",
                "description": "Mit lát, hall, szagol a belépő? 3–5 mondat érzéki leírás.",
            },
            "atmosphere": {
                "type": "string",
                "description": "Általános hangulat, légkör 1–2 mondatban.",
            },
            "layout": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Fontosabb helyek, szobák, területek listája (3–6 elem).",
            },
            "current_scene": {
                "type": "string",
                "description": "Mi történik éppen most a helyszínen? 2–3 mondat.",
            },
            "notable_details": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Érdekes részletek, amikre a játékosok figyelhetnek (2–4 elem).",
            },
            "npc_presence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {
                            "type": "string",
                            "description": "Szerep/foglalkozás (pl. fogadós, őr, titokzatos alak)",
                        },
                        "importance": {
                            "type": "string",
                            "enum": ["minor", "moderate", "major"],
                        },
                        "brief": {
                            "type": "string",
                            "description": "Egy mondat a megjelenéséről vagy viselkedéséről",
                        },
                    },
                    "required": ["role", "importance", "brief"],
                },
                "description": "Kik tartózkodnak a helyszínen (1–4 NPC).",
            },
            "dm_notes": {
                "type": "string",
                "description": "Mesélőnek szóló megjegyzések, rejtett infók, lehetséges szálak.",
            },
        },
        "required": [
            "sensory_description", "atmosphere", "current_scene", "npc_presence"
        ],
    },
}


# ---------------------------------------------------------------------------
# AI location description call
# ---------------------------------------------------------------------------

def _generate_description(
    location_context: str,
    system_blocks: list[dict],
    client: anthropic.Anthropic,
) -> dict:
    user_msg = (
        f"{location_context}\n\n"
        "Generáld le a helyszín részletes leírását és döntsd el, "
        "kik tartózkodnak most itt. A hangulat és NPC-k legyenek "
        "összhangban a helyszín jellegével."
    )
    logger.info("Location description call — context_len={n}", n=len(location_context))
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=system_blocks,
        tools=[_LOCATION_TOOL],
        tool_choice={"type": "tool", "name": "describe_location"},
        messages=[{"role": "user", "content": user_msg}],
    )
    log_claude_call(
        stage="location_desc",
        model=MODEL,
        system_blocks=system_blocks,
        messages=[{"role": "user", "content": user_msg}],
        response=response,
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "describe_location":
            return block.input

    raise RuntimeError("Location description returned no tool call")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_location(
    location_name: str,
    races_data: dict,
    classes_data: dict,
    client: anthropic.Anthropic,
) -> dict:
    """
    Full location generation pipeline.

    Returns a dict with:
      location_data  — raw JSON entry (or None)
      description    — AI-generated scene
      npcs           — list of fully generated NPC dicts
    """
    existing_data    = _load_location_data(location_name)
    location_context = _location_context_str(location_name, existing_data)

    # System blocks for location description use the location skill prompt
    system_blocks = _world_system_blocks(races_data, classes_data, skill_text=_LOCATION_SKILL)

    # Step 1 — generate location description + decide which NPCs are present
    description = _generate_description(location_context, system_blocks, client)

    # Step 2 — generate each NPC the AI requested
    npcs: list[dict] = []
    for npc_spec in description.get("npc_presence", []):
        role_hint = npc_spec.get("role", "ismeretlen") + " — " + npc_spec.get("brief", "")
        try:
            npc = generate_npc(
                location_context = location_context,
                role_hint        = role_hint,
                races_data       = races_data,
                classes_data     = classes_data,
                client           = client,
            )
            npc["spec"] = npc_spec
            npcs.append(npc)
        except Exception as exc:          # pylint: disable=broad-except
            npcs.append({"spec": npc_spec, "error": str(exc)})

    return {
        "name":          location_name,
        "location_data": existing_data,
        "description":   description,
        "npcs":          npcs,
    }
