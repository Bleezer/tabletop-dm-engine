"""
MAGUS NPC generator — two-stage AI pipeline.

Stage 1 (AI)   : decide race, class, level, role for the location context
Stage 2 (code)  : calculate stats from the decision
Stage 3 (AI)   : generate personality, appearance, background from the numbers

World data (races + classes) is sent in the system prompt with cache_control
so it is only billed once every 5 minutes across repeated calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anthropic

from engine.magus.stats_helpers import build_stat_block, format_stat_block

ROOT    = Path(__file__).parent.parent.parent
MODEL   = "claude-sonnet-4-6"


def _load_skill(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


_NPC_SKILL = _load_skill(ROOT / "skills" / "npc_generator.md")


# ---------------------------------------------------------------------------
# World-data summaries  (injected into system prompt, then cached)
# ---------------------------------------------------------------------------

def _races_summary(races_data: dict) -> str:
    lines = ["### Elérhető fajok"]
    for race in races_data['races']:
        mods = race.get('stat_modifiers', {})
        mod_str = ', '.join(
            f"{k}:{'+' if v > 0 else ''}{v}" for k, v in mods.items()
        ) or 'nincs módosító'
        classes = [c['name'] for c in race.get('available_classes', [])]
        cls_str = ', '.join(classes[:6]) + ('...' if len(classes) > 6 else '')
        lines.append(f"- **{race['name']}** | módosítók: {mod_str} | kasztok: {cls_str}")
    return '\n'.join(lines)


def _classes_summary(classes_data: dict) -> str:
    lines = ["### Elérhető kasztok (válogatás)"]
    seen: set[str] = set()
    for cls in classes_data['kasztok']:
        name = cls['nev']
        if name in seen:
            continue
        seen.add(name)
        h  = cls.get('harcertekek', {})
        ep = cls.get('ep', {})
        lines.append(
            f"- **{name}** | KÉ {h.get('ke','?')} TÉ {h.get('te','?')} "
            f"VÉ {h.get('ve','?')} | ÉP {ep.get('alap','?')}+{ep.get('szintenként','?')}/szint"
        )
    return '\n'.join(lines)


def _world_system_blocks(
    races_data: dict,
    classes_data: dict,
    skill_text: str = _NPC_SKILL,
) -> list[dict]:
    """
    Two system blocks:
      1. Stable world data  → cache_control ephemeral  (shared across calls)
      2. Role instruction   → loaded from skills/npc_generator.md (no cache)
    """
    world_text = (
        "# MAGUS RPG — Világadat (Ynev, Hetedkor)\n\n"
        + _races_summary(races_data)
        + "\n\n"
        + _classes_summary(classes_data)
    )
    role_text = skill_text if skill_text else (
        "Te egy tapasztalt MAGUS RPG Mesélő vagy. "
        "Minden NPC-t a MAGUS világ hangulatához igazítva alkotsz meg. "
        "Válaszaidat mindig az előírt JSON tool formátumban add meg."
    )
    return [
        {
            "type": "text",
            "text": world_text,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": role_text,
        },
    ]


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

_CONCEPT_TOOL: dict[str, Any] = {
    "name": "define_npc_concept",
    "description": (
        "A helyszín és szerep alapján döntsd el az NPC alapadatait: "
        "faj, kaszt, szint, fontossági szint és a pontkerete."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "race": {
                "type": "string",
                "description": "Faj neve pontosan a fajlistából",
            },
            "class_name": {
                "type": "string",
                "description": "Kaszt neve pontosan a kasztlistából",
            },
            "level": {
                "type": "integer",
                "minimum": 1,
                "maximum": 15,
                "description": "1–15 közötti szint; 1–3 novícius, 4–7 tapasztalt, 8+ mester",
            },
            "role": {
                "type": "string",
                "description": "Funkció a helyszínen (pl. fogadós, őr, tolvaj, kereskedő)",
            },
            "importance": {
                "type": "string",
                "enum": ["minor", "moderate", "major"],
                "description": "minor=statiszta 130p, moderate=mellékszereplő 140p, major=főszereplő 150p",
            },
            "point_pool": {
                "type": "integer",
                "minimum": 130,
                "maximum": 150,
                "description": "Összpont: minor=130, moderate=140, major=150",
            },
        },
        "required": ["race", "class_name", "level", "role", "importance", "point_pool"],
    },
}

_CHARACTER_TOOL: dict[str, Any] = {
    "name": "create_npc_character",
    "description": "A statisztikák alapján generáld az NPC személyiségét, megjelenését és hátterét.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Ynev-hez illő név"},
            "gender": {"type": "string", "enum": ["férfi", "nő", "ismeretlen"]},
            "age_description": {
                "type": "string",
                "description": "Korleírás (pl. 'középkorú', 'idős', 'fiatal')",
            },
            "appearance": {
                "type": "string",
                "description": "Részletes fizikai leírás 2–3 mondatban",
            },
            "personality": {
                "type": "string",
                "description": "Személyiség, jellem, viselkedésmód 2–3 mondatban",
            },
            "background": {
                "type": "string",
                "description": "Rövid háttér, hogyan került ide 1–2 mondatban",
            },
            "speech_style": {
                "type": "string",
                "description": "Hogyan beszél, jellegzetes szófordulatok, hangsúly",
            },
            "motivation": {
                "type": "string",
                "description": "Fő motiváció, mit akar elérni",
            },
            "secret": {
                "type": "string",
                "description": "Egy titok vagy rejtett szempont (opcionális)",
            },
            "attitude_to_strangers": {
                "type": "string",
                "enum": ["barátságos", "semleges", "gyanakvó", "ellenséges"],
            },
        },
        "required": [
            "name", "gender", "age_description", "appearance",
            "personality", "background", "speech_style",
            "motivation", "attitude_to_strangers",
        ],
    },
}


# ---------------------------------------------------------------------------
# Single-call NPC generation (concept → stats injected → character)
# ---------------------------------------------------------------------------

def _generate_npc_single_call(
    location_context: str,
    role_hint: str,
    races_data: dict,
    classes_data: dict,
    system_blocks: list[dict],
    client: anthropic.Anthropic,
) -> tuple[dict, dict, dict]:
    """
    One conversation, two tool calls:
      turn 1 → AI picks concept (define_npc_concept)
      code   → build_stat_block from concept
      turn 2 → AI generates character (create_npc_character), stat summary injected as tool result
    Returns (concept, stat_block, character).
    """
    user_msg = (
        f"Helyszín:\n{location_context}\n\n"
        f"Szerep hint: {role_hint}\n\n"
        "Először döntsd el az NPC alapadatait (faj, kaszt, szint, szerep, fontosság), "
        "majd a kapott statisztikák alapján alkoss meg egy hiteles karaktert."
    )

    # Turn 1 — concept
    r1 = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=system_blocks,
        tools=[_CONCEPT_TOOL, _CHARACTER_TOOL],
        tool_choice={"type": "tool", "name": "define_npc_concept"},
        messages=[{"role": "user", "content": user_msg}],
    )

    concept = None
    concept_tool_use_id = None
    for block in r1.content:
        if block.type == "tool_use" and block.name == "define_npc_concept":
            concept = block.input
            concept_tool_use_id = block.id
            break

    if concept is None:
        raise RuntimeError("NPC concept generation returned no tool call")

    # Code: calculate stats
    stat_block = build_stat_block(
        race_name    = concept["race"],
        class_name   = concept["class_name"],
        level        = concept["level"],
        total_points = concept["point_pool"],
        races_data   = races_data,
        classes_data = classes_data,
    )
    stat_summary = format_stat_block(stat_block)

    # Turn 2 — character (continuing the same conversation)
    r2 = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=system_blocks,
        tools=[_CONCEPT_TOOL, _CHARACTER_TOOL],
        tool_choice={"type": "tool", "name": "create_npc_character"},
        messages=[
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": r1.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": concept_tool_use_id,
                        "content": (
                            f"Alapadatok elfogadva. Kiszámított statisztikák:\n{stat_summary}\n\n"
                            "Most alkoss meg egy hiteles MAGUS-stílusú karaktert ezekre a számokra alapozva. "
                            "A statisztikák tükröződjenek a személyiségben."
                        ),
                    }
                ],
            },
        ],
    )

    character = None
    for block in r2.content:
        if block.type == "tool_use" and block.name == "create_npc_character":
            character = block.input
            break

    if character is None:
        raise RuntimeError("NPC character generation returned no tool call")

    return concept, stat_block, character


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_npc(
    location_context: str,
    role_hint: str,
    races_data: dict,
    classes_data: dict,
    client: anthropic.Anthropic,
) -> dict:
    """
    NPC generation: concept + character in a single two-turn conversation.
    Returns a dict with concept, stat_block, and character.
    """
    system_blocks = _world_system_blocks(races_data, classes_data)

    concept, stat_block, character = _generate_npc_single_call(
        location_context = location_context,
        role_hint        = role_hint,
        races_data       = races_data,
        classes_data     = classes_data,
        system_blocks    = system_blocks,
        client           = client,
    )

    return {
        "concept":    concept,
        "stat_block": stat_block,
        "character":  character,
    }
