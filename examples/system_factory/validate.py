"""Validation for specs and generated projects.

Two layers:
- ``validate_spec``: referential integrity of a ``SystemSpec`` (tasks reference real agents, no
  unknown/cyclic task dependencies, tools reference declared MCP servers).
- ``check_generated_python``: every generated ``*.py`` file compiles (``compile()``), so we never
  hand back a project that fails at import time.
"""

from __future__ import annotations

from .spec import SystemSpec


class SpecValidationError(ValueError):
    """Raised when a SystemSpec is internally inconsistent."""


def validate_spec(spec: SystemSpec) -> None:
    agent_names = spec.agent_names()
    if not spec.agents:
        raise SpecValidationError("System has no agents.")
    if not spec.tasks:
        raise SpecValidationError("System has no tasks.")

    server_names = {s.name for s in spec.mcp_servers}
    task_ids = {t.id for t in spec.tasks}

    for task in spec.tasks:
        if task.agent not in agent_names:
            raise SpecValidationError(f"Task {task.id!r} references unknown agent {task.agent!r}.")
        for dep in task.depends_on:
            if dep not in task_ids:
                raise SpecValidationError(f"Task {task.id!r} depends on unknown task {dep!r}.")

    for agent in spec.agents:
        for tool in agent.tools:
            # Tools may be built-ins; we only flag an mcp-looking tool that isn't declared.
            if tool.startswith("mcp:") and tool[4:] not in server_names:
                raise SpecValidationError(
                    f"Agent {agent.name!r} uses MCP tool {tool!r} but no such server is declared."
                )

    _check_task_cycles(spec)


def _check_task_cycles(spec: SystemSpec) -> None:
    by_id = {t.id: t for t in spec.tasks}
    resolved: set[str] = set()

    def visit(tid: str, stack: frozenset[str]) -> None:
        if tid in resolved:
            return
        if tid in stack:
            raise SpecValidationError(f"Dependency cycle detected involving task {tid!r}.")
        for dep in by_id[tid].depends_on:
            visit(dep, stack | {tid})
        resolved.add(tid)

    for task in spec.tasks:
        visit(task.id, frozenset())


def check_generated_python(files: dict[str, str]) -> list[str]:
    """Return a list of error messages for any generated ``*.py`` that fails to compile."""
    errors: list[str] = []
    for path, content in files.items():
        if not path.endswith(".py"):
            continue
        try:
            compile(content, path, "exec")
        except SyntaxError as exc:  # pragma: no cover - exercised via tests with bad input
            errors.append(f"{path}: {exc}")
    return errors
