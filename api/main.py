"""
FastAPI application — DM Engine backend.

Run:
    uvicorn api.main:app --reload --port 8000
"""

import time

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.magus import router as magus_router
from engine.magus.core.logger import get_logger

logger = get_logger("api")

app = FastAPI(title="DM Engine API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    if request.url.path != "/health":
        logger.info(
            "{method} {path} → {status} ({ms:.0f}ms)",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            ms=ms,
        )
    return response


app.include_router(magus_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
