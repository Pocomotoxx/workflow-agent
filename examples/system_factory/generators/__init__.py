"""Pluggable backends that turn a ``SystemSpec`` into a runnable project."""

from __future__ import annotations

from .agents_python_backend import AgentsPythonBackend
from .base import Backend
from .crewai_backend import CrewAIBackend

BACKENDS: dict[str, Backend] = {
    "crewai": CrewAIBackend(),
    "agents-python": AgentsPythonBackend(),
}


def get_backend(name: str) -> Backend:
    try:
        return BACKENDS[name]
    except KeyError:
        raise ValueError(
            f"Unknown backend {name!r}. Available: {', '.join(sorted(BACKENDS))}."
        ) from None


__all__ = ["Backend", "CrewAIBackend", "AgentsPythonBackend", "BACKENDS", "get_backend"]
