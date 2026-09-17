"""System factory: task -> architect -> SystemSpec -> generated project -> static presentation.

This is the meta-agent pipeline. It designs a multi-agent system from a natural-language task,
generates a runnable project for a chosen backend (CrewAI or the Agents SDK), validates it, and
produces a static presentation. A *live* run of the generated system is intentionally NOT part of
this pipeline -- it is offered separately and only after explicit approval (see ``sandbox.py``).

Secrets are never handled here: the spec and generated files reference env var names only.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path

from agents import Runner, set_tracing_disabled
from agents.models.interface import Model

from .architect import build_architect
from .demo import presentation
from .generators import get_backend
from .spec import SystemSpec
from .validate import check_generated_python, validate_spec

# Provider-agnostic and no OpenAI credentials needed for tracing.
set_tracing_disabled(disabled=True)


@dataclass
class GeneratedProject:
    spec: SystemSpec
    backend_name: str
    files: dict[str, str]
    presentation_md: str

    def write_to(self, out_dir: str | Path) -> Path:
        """Materialize the generated files under ``out_dir/<spec.name>`` and return that path."""
        root = Path(out_dir) / self.spec.name
        for rel, content in self.files.items():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        (root / "PRESENTATION.md").write_text(self.presentation_md, encoding="utf-8")
        return root


async def build_system(
    task: str,
    *,
    backend: str = "agents-python",
    model: str | Model | None = None,
    mcp_hint: str = "",
) -> GeneratedProject:
    """Design and generate a system for ``task``. Pass ``model`` (e.g. a ScriptedModel) for tests."""
    backend_impl = get_backend(backend)

    architect = build_architect(model)
    prompt = task if not mcp_hint else f"{task}\n\nAvailable MCP servers / access:\n{mcp_hint}"
    result = await Runner.run(architect, prompt)
    spec = result.final_output
    assert isinstance(spec, SystemSpec)

    validate_spec(spec)
    files = backend_impl.generate(spec)

    errors = check_generated_python(files)
    if errors:
        raise RuntimeError("Generated project failed validation:\n" + "\n".join(errors))

    return GeneratedProject(
        spec=spec,
        backend_name=backend_impl.name,
        files=files,
        presentation_md=presentation(spec, backend_impl.name, files),
    )


async def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Design and generate a multi-agent system.")
    parser.add_argument("task", nargs="+", help="What the system should do.")
    parser.add_argument("--backend", default="agents-python", choices=["agents-python", "crewai"])
    parser.add_argument("--out", default="generated", help="Output directory.")
    parser.add_argument("--mcp", default="", help="Optional MCP servers / access notes.")
    args = parser.parse_args()

    project = await build_system(" ".join(args.task), backend=args.backend, mcp_hint=args.mcp)
    root = project.write_to(args.out)
    print(project.presentation_md)
    print(f"\nGenerated {len(project.files)} file(s) under: {root}")
    print(
        "Review it, then run a live sandboxed demo explicitly (see examples/system_factory/README.md)."
    )


if __name__ == "__main__":
    asyncio.run(_main())
