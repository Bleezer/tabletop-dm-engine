"""
MAGUS archetype persistence.

Archetypes are class-independent skill priority lists.
Users define which skills to buy first when distributing KP,
regardless of character class.

list_archetipusok   — all archetypes (summary)
get_archetipus      — single archetype with full skill list
create_archetipus   — insert new archetype
update_archetipus   — replace name/description/skill list
delete_archetipus   — remove archetype by id
list_kepzettsegek   — all skills (for dropdown population)
"""
from __future__ import annotations

from pathlib import Path

from engine.magus.core.db import DB_PATH, get_connection


def list_archetipusok(db_path: Path = DB_PATH) -> list[dict]:
    """Return all archetypes ordered by name, with skill count."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT a.id, a.nev, a.leiras, a.ikon,
                   COUNT(ak.id) AS kepzettseg_szam,
                   a.letrehozva, a.frissitve
            FROM archetipusok a
            LEFT JOIN archetipus_kepzettsegek ak ON ak.archetipus_id = a.id
            GROUP BY a.id
            ORDER BY a.nev
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_archetipus(archetipus_id: int, db_path: Path = DB_PATH) -> dict:
    """Return archetype with its full ordered skill list."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT id, nev, leiras, ikon, letrehozva, frissitve FROM archetipusok WHERE id = ?",
            (archetipus_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Nem található archetípus: id={archetipus_id}")

        result = dict(row)

        skills = conn.execute(
            """
            SELECT ak.id, ak.prioritas, ak.cel_fok,
                   ke.id AS kepzettseg_id, ke.nev, ke.tipus, ke.kategoria,
                   ke.ar_alapfok, ke.ar_mesterfok
            FROM archetipus_kepzettsegek ak
            JOIN kepzettsegek ke ON ke.id = ak.kepzettseg_id
            WHERE ak.archetipus_id = ?
            ORDER BY ak.prioritas
            """,
            (archetipus_id,),
        ).fetchall()
        result["kepzettsegek"] = [dict(s) for s in skills]
        return result
    finally:
        conn.close()


def create_archetipus(
    nev: str,
    leiras: str | None,
    kepzettsegek: list[dict],
    ikon: str = '⚔',
    db_path: Path = DB_PATH,
) -> int:
    """
    Insert a new archetype and its skill list.

    kepzettsegek items: {"kepzettseg_id": int, "cel_fok": str}
    Priority is assigned by list position (0-based).

    Returns the new archetype id.
    """
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO archetipusok (nev, leiras, ikon) VALUES (?, ?, ?)",
            (nev, leiras, ikon),
        )
        new_id = cur.lastrowid
        _replace_skills(conn, new_id, kepzettsegek)
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_archetipus(
    archetipus_id: int,
    nev: str,
    leiras: str | None,
    kepzettsegek: list[dict],
    ikon: str = '⚔',
    db_path: Path = DB_PATH,
) -> None:
    """
    Replace the name, description, ikon, and full skill list of an archetype.

    Raises ValueError if the archetype does not exist.
    """
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "UPDATE archetipusok SET nev = ?, leiras = ?, ikon = ?, frissitve = datetime('now') WHERE id = ?",
            (nev, leiras, ikon, archetipus_id),
        )
        if cur.rowcount == 0:
            raise ValueError(f"Nem található archetípus: id={archetipus_id}")
        _replace_skills(conn, archetipus_id, kepzettsegek)
        conn.commit()
    finally:
        conn.close()


def delete_archetipus(archetipus_id: int, db_path: Path = DB_PATH) -> bool:
    """Delete archetype and its skills (CASCADE). Returns True if deleted."""
    conn = get_connection(db_path)
    try:
        cur = conn.execute("DELETE FROM archetipusok WHERE id = ?", (archetipus_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def list_kepzettsegek(db_path: Path = DB_PATH) -> list[dict]:
    """Return all skills ordered by category then name (for dropdown population)."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, nev, kategoria, tipus, ar_alapfok, ar_mesterfok
            FROM kepzettsegek
            ORDER BY kategoria, nev
            """
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _replace_skills(conn, archetipus_id: int, kepzettsegek: list[dict]) -> None:
    """Delete existing skills and insert new ones with positional priority."""
    conn.execute(
        "DELETE FROM archetipus_kepzettsegek WHERE archetipus_id = ?",
        (archetipus_id,),
    )
    for i, item in enumerate(kepzettsegek):
        conn.execute(
            """
            INSERT INTO archetipus_kepzettsegek (archetipus_id, kepzettseg_id, prioritas, cel_fok)
            VALUES (?, ?, ?, ?)
            """,
            (archetipus_id, item["kepzettseg_id"], i, item.get("cel_fok", "alap")),
        )
