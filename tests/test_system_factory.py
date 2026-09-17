"""Offline tests for the system-factory meta-agent example.

The architect's LLM call is driven by a ScriptedModel, so these make no provider calls. They verify
the full pipeline: spec -> validate -> generate (both backends) -> compile-check -> presentation,
plus spec validation errors and the sandbox opt-in guard.
"""

from __future__ import annotations

import json

import pytest

from agents.testing.model import ScriptedModel
from examples.system_factory import build_system
from examples.system_factory.sandbox import SandboxRefused, run_generated
from examples.system_factory.spec import AgentSpec, SystemSpec, TaskSpec
from examples.system_factory.validate import SpecValidationError, validate_spec
from tests.test_responses import get_text_message

SPEC = {
    "name": "market_research_crew",
    "description": "Researches a market and writes a competitive brief.",
    "provider_env": "AGENTS_DEFAULT_PROVIDER",
    "model_env": "AGENTS_DEFAULT_MODEL",
    "required_env": ["TAVILY_API_KEY"],
    "agents": [
        {
            "name": "researcher",
            "role": "Research Analyst",
            "goal": "Gather market facts",
            "backstory": "Meticulous.",
            "tools": [],
        },
        {
            "name": "writer",
            "role": "Brief Writer",
            "goal": "Write the brief",
            "backstory": "",
            "tools": [],
        },
    ],
    "tasks": [
        {
            "id": "t1",
            "description": "Research the market.",
            "agent": "researcher",
            "expected_output": "Facts.",
            "depends_on": [],
        },
        {
            "id": "t2",
            "description": "Write the brief.",
            "agent": "writer",
            "expected_output": "A brief.",
            "depends_on": ["t1"],
        },
    ],
    "mcp_servers": [],
}


def _scripted() -> ScriptedModel:
    return ScriptedModel([[get_text_message(json.dumps(SPEC))]])


@pytest.mark.asyncio
@pytest.mark.parametrize("backend", ["agents-python", "crewai"])
async def test_build_system_generates_valid_project(backend: str) -> None:
    project = await build_system(
        "Build a market research system", backend=backend, model=_scripted()
    )

    assert project.spec.name == "market_research_crew"
    assert project.backend_name == backend
    # Every generated project has a README and an .env.example (names only, no values).
    assert "README.md" in project.files
    assert ".env.example" in project.files
    assert "TAVILY_API_KEY=" in project.files[".env.example"]
    assert "sk-" not in project.files[".env.example"]  # never emit secret values

    # Presentation includes a Mermaid diagram and the task edge t1 -> t2.
    assert "```mermaid" in project.presentation_md
    assert "t1 --> t2" in project.presentation_md

    # Generated Python compiles (build_system already compile-checks; assert the entry exists).
    entry = "agent_system.py" if backend == "agents-python" else "crew.py"
    assert entry in project.files
    compile(project.files[entry], entry, "exec")


@pytest.mark.asyncio
async def test_write_to_materializes_files(tmp_path) -> None:
    project = await build_system("x", backend="crewai", model=_scripted())
    root = project.write_to(tmp_path)
    assert (root / "crew.py").exists()
    assert (root / "PRESENTATION.md").exists()
    assert (root / ".env.example").exists()


def test_validate_spec_rejects_unknown_agent() -> None:
    spec = SystemSpec(
        name="x",
        description="",
        agents=[AgentSpec(name="a", role="r", goal="g")],
        tasks=[TaskSpec(id="t1", description="", agent="ghost")],
    )
    with pytest.raises(SpecValidationError, match="unknown agent"):
        validate_spec(spec)


def test_validate_spec_rejects_cycle() -> None:
    spec = SystemSpec(
        name="x",
        description="",
        agents=[AgentSpec(name="a", role="r", goal="g")],
        tasks=[
            TaskSpec(id="t1", description="", agent="a", depends_on=["t2"]),
            TaskSpec(id="t2", description="", agent="a", depends_on=["t1"]),
        ],
    )
    with pytest.raises(SpecValidationError, match="cycle"):
        validate_spec(spec)


def test_sandbox_refuses_without_confirmation(tmp_path) -> None:
    with pytest.raises(SandboxRefused):
        run_generated(tmp_path, "agents-python")
