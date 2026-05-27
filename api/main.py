"""
FastAPI application — DM Engine backend.

Run:
    uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.magus import router as magus_router

app = FastAPI(title="DM Engine API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(magus_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
