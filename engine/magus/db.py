"""
SQLite connection helpers — one .db file per RPG system.

  MAGUS    → world/magus/magus.db
  Star Wars → world/starwars/starwars.db  (future)
  D&D      → world/dnd/dnd.db             (future)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT        = Path(__file__).parent.parent.parent
DB_PATH     = ROOT / "world" / "magus" / "magus.db"
_SCHEMA_SQL = ROOT / "world" / "magus" / "schema.sql"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    """Create all tables from schema.sql if they don't exist yet."""
    sql = _SCHEMA_SQL.read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(sql)
    finally:
        conn.close()
