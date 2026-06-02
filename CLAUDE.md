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
- UI / visual style (MAGUS dark fantasy theme): see /skills/magus_ui_style.md — use this whenever modifying frontend styling, CSS, layout or visual components

## Szerverek kezelése

Backend: `uvicorn api.main:app --reload --host 0.0.0.0 --port 8000` (projekt gyökérből, háttérben)
Frontend: `cd frontend && npm run dev` (Vite, port 5173, háttérben)

Szabályok:
1. Session elején: ellenőrizd, hogy fut-e mindkét szerver. Ha nem, indítsd el.
2. Python fájl módosítás után: uvicorn --reload automatikusan frissít, nincs teendő.
3. World JSON fájl módosítás után (`/world/` alatt): indítsd újra a backend szervert.
4. Frontend fájl módosítás után: Vite HMR automatikusan frissít, nincs teendő.