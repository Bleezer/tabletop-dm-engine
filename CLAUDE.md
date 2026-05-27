Project name: Star Wars AI Dungeon Master Engine

Description: A modular AI-powered dungeon master assistant for tabletop RPG sessions using the Star Wars RPG ruleset. The AI handles NPC behavior, encounter generation, and narrative adaptation while keeping rules and world data separate from core logic.
Tech stack: Python, FastAPI backend, React frontend
Architecture:

/rules/ - ruleset definitions, separate from core logic, swappable
/world/ - world data, locations, NPCs, descriptions
/engine/ - core DM logic, encounter generation, character handling
/api/ - FastAPI endpoints
/frontend/ - React web client

Key principles:

Rules and world data must be completely separated from engine logic
Portable - easy to swap rulesets or worlds
AI-driven nuances, not AI-driven story

## Skills
- Location generation: see /skills/location_generator.md
- NPC generation: see /skills/npc_generator.md