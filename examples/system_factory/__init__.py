"""System factory: a meta-agent that designs, generates, and presents multi-agent systems.

See README.md. Public entry points:
- ``build_system(task, backend=...)`` -> ``GeneratedProject``
- ``GeneratedProject.write_to(dir)``
- ``sandbox.run_generated(dir, backend, confirm=True)`` for an opt-in live run.
"""

from __future__ import annotations

from .factory import GeneratedProject, build_system
from .spec import AgentSpec, MCPServerSpec, SystemSpec, TaskSpec

__all__ = [
    "build_system",
    "GeneratedProject",
    "SystemSpec",
    "AgentSpec",
    "TaskSpec",
    "MCPServerSpec",
]
