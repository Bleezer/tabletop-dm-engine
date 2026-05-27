"""
FastAPI router for MAGUS DM engine endpoints.

POST   /api/magus/location         — generate location + NPCs
POST   /api/magus/npc              — generate NPC (auto-saved to DB, returns id)
GET    /api/magus/karakterek       — list saved characters
GET    /api/magus/karakterek/{id}  — get single character
PATCH  /api/magus/karakterek/{id}  — update fields (nev, elotortenete, celok, …)
DELETE /api/magus/karakterek/{id}  — delete character
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from engine.magus.pipeline import generate
from engine.magus.npc_generator import generate_npc
from engine.magus.pipeline import _load_json, _RACES_FILE, _CLASSES_FILE
from engine.magus.karakter import (
    save_from_npc_result,
    load_karakter,
    list_karakterek,
    row_to_npc,
    update_karakter,
    delete_karakter,
)

import anthropic
import os

router = APIRouter(prefix="/api/magus", tags=["magus"])


def _client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY nincs beállítva")
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class LocationRequest(BaseModel):
    location_name: str


class NpcRequest(BaseModel):
    location_context: str = ""
    role_hint: str


class KarakterPatch(BaseModel):
    nev: str | None = None
    nem: str | None = None
    kor_leiras: str | None = None
    megjelenes: str | None = None
    szemelyiseg: str | None = None
    elotortenete: str | None = None
    szolasmod: str | None = None
    motivacio: str | None = None
    titok: str | None = None
    idegenekhez_viszonyulas: str | None = None
    felszereles: list | None = None
    celok: list | None = None
    megjegyzesek: str | None = None


# ---------------------------------------------------------------------------
# Generation endpoints
# ---------------------------------------------------------------------------

@router.post("/location")
async def location_endpoint(req: LocationRequest) -> dict:
    if not req.location_name.strip():
        raise HTTPException(status_code=422, detail="location_name nem lehet üres")
    try:
        result = generate(req.location_name.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result


@router.post("/npc")
async def npc_endpoint(req: NpcRequest) -> dict:
    if not req.role_hint.strip():
        raise HTTPException(status_code=422, detail="role_hint nem lehet üres")
    try:
        client       = _client()
        races_data   = _load_json(_RACES_FILE)
        classes_data = _load_json(_CLASSES_FILE)
        result = generate_npc(
            location_context = req.location_context.strip(),
            role_hint        = req.role_hint.strip(),
            races_data       = races_data,
            classes_data     = classes_data,
            client           = client,
        )
        kid = save_from_npc_result(result)
        return {**result, "id": kid}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Character CRUD
# ---------------------------------------------------------------------------

@router.get("/karakterek")
async def list_endpoint() -> list[dict]:
    try:
        return list_karakterek()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/karakterek/{karakter_id}")
async def get_endpoint(karakter_id: int) -> dict:
    try:
        row = load_karakter(karakter_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Karakter nem található: {karakter_id}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return row_to_npc(row)


@router.patch("/karakterek/{karakter_id}")
async def patch_endpoint(karakter_id: int, body: KarakterPatch) -> dict:
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=422, detail="Nincs frissítendő mező")
    try:
        update_karakter(karakter_id, **fields)
        row = load_karakter(karakter_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Karakter nem található: {karakter_id}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return row_to_npc(row)


@router.delete("/karakterek/{karakter_id}")
async def delete_endpoint(karakter_id: int) -> dict:
    try:
        deleted = delete_karakter(karakter_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Karakter nem található: {karakter_id}")
    return {"deleted": karakter_id}
