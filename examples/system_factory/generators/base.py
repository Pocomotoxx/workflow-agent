"""Backend protocol and shared helpers for project generation."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..spec import SystemSpec


@runtime_checkable
class Backend(Protocol):
    """Turns a framework-neutral ``SystemSpec`` into a map of {relative path: file content}."""

    name: str

    def generate(self, spec: SystemSpec) -> dict[str, str]:
        """Return the files of a runnable project. Paths are POSIX-relative to the project root."""
        ...


def env_example(spec: SystemSpec) -> str:
    """Render an ``.env.example`` listing required env var *names* only (never values)."""
    lines = [
        "# Copy to .env and fill in your own values. Never commit real secrets.",
        f"{spec.provider_env}=litellm",
        f"{spec.model_env}=anthropic/claude-sonnet-4-20250514",
    ]
    for name in spec.required_env:
        lines.append(f"{name}=")
    return "\n".join(lines) + "\n"


def py_str(value: str) -> str:
    """Safe Python string literal for embedding user/LLM text into generated code."""
    return repr(value)
