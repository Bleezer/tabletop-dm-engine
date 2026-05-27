"""
Ruleset loader — generic interface and JSON implementation.

The Ruleset ABC is intentionally thin: name, version, and get().
System-specific engines (genesys/, dnd/, …) call get() with their own
key paths and interpret the data themselves.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Abstract interface  (system-agnostic)
# ---------------------------------------------------------------------------

class Ruleset(ABC):
    """
    Minimal contract every ruleset must satisfy.
    Engines read game data via get() — no system-specific methods live here.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable ruleset name."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Ruleset version string."""
        ...

    @abstractmethod
    def get(self, *path: str) -> Any:
        """
        Retrieve a nested value by sequential string keys.
        Raises KeyError with a descriptive message if the path does not exist.

        Example: ruleset.get("turn_actions", "maneuvers", "limit")
        """
        ...

    def __repr__(self) -> str:
        return f"<Ruleset name={self.name!r} version={self.version!r}>"


# ---------------------------------------------------------------------------
# JSON implementation
# ---------------------------------------------------------------------------

class JsonRuleset(Ruleset):
    """Loads any JSON file as a ruleset; all data accessible via get()."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)
        with open(self._path, encoding="utf-8") as f:
            self._data: dict = json.load(f)

    @property
    def name(self) -> str:
        return self._data.get("ruleset", self._path.stem)

    @property
    def version(self) -> str:
        return self._data.get("version", "unknown")

    def get(self, *path: str) -> Any:
        node: Any = self._data
        for key in path:
            try:
                node = node[key]
            except (KeyError, TypeError) as exc:
                raise KeyError(
                    f"Ruleset '{self.name}': path {path!r} failed at key '{key}'"
                ) from exc
        return node


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_registry: dict[str, Path] = {}
_default_name: str | None  = None


def register(name: str, path: Path | str) -> None:
    """Associate a ruleset name with a file path.
    The first registration automatically becomes the default."""
    global _default_name
    _registry[name] = Path(path)
    if _default_name is None:
        _default_name = name


def set_default(name: str) -> None:
    """Override which registered ruleset get_default() returns."""
    global _default_name
    if name not in _registry:
        available = ", ".join(_registry) or "(none registered)"
        raise KeyError(f"Unknown ruleset '{name}'. Available: {available}")
    _default_name = name


def get_default() -> Ruleset:
    """Load and return the current default ruleset."""
    if _default_name is None:
        raise RuntimeError(
            "No default ruleset set. Call register() or set_default() first."
        )
    return load(_default_name)


def load(name: str) -> Ruleset:
    """Load a registered ruleset by name."""
    if name not in _registry:
        available = ", ".join(_registry) or "(none registered)"
        raise KeyError(f"Unknown ruleset '{name}'. Available: {available}")
    return load_from_path(_registry[name])


def load_from_path(path: Path | str) -> Ruleset:
    """Load a ruleset directly from a file path, bypassing the registry."""
    return JsonRuleset(Path(path))


def registered_names() -> list[str]:
    """Return all currently registered ruleset names."""
    return list(_registry.keys())


# ---------------------------------------------------------------------------
# Built-in registrations  (add new rulesets here, never in engine code)
# ---------------------------------------------------------------------------

_BUILTIN_DIR = Path(__file__).parent
register("starwars_core", _BUILTIN_DIR / "starwars_core.json")
