"""Specialist agents for the workflow orchestrator example.

These port the specialist roles from the Claude Code "workflow orchestration" plugin
(https://github.com/Pocomotoxx/claude-code-workflow-orchestration) into provider-agnostic
Agents SDK ``Agent`` objects. In that plugin each specialist is a Claude Code subagent defined in
markdown and activated by the Claude Code runtime; here each is a plain ``Agent`` whose behavior is
its ``instructions`` string, runnable against any provider the SDK supports.

No ``model=`` is set on any agent, so they use the configured default provider/model
(``AGENTS_DEFAULT_PROVIDER`` / ``AGENTS_DEFAULT_MODEL``, or OpenAI by default).
"""

from __future__ import annotations

from agents import Agent
from agents.models.interface import Model

# Each specialist returns a short, self-contained deliverable as plain text. The orchestrator feeds
# a phase description (plus upstream results) as input and collects the final_output as an artifact.
_SPECIALIST_SPECS: dict[str, str] = {
    "codebase-context-analyzer": (
        "You analyze codebase structure, patterns, dependencies, and architecture. "
        "Given a task, explain how the relevant parts work, where things are implemented, and "
        "which constraints or conventions matter. Produce a concise, factual briefing."
    ),
    "tech-lead-architect": (
        "You are a tech lead and software architect. You design implementation approaches, "
        "evaluate technology choices, and make technical decisions with clear trade-offs. "
        "Produce a concrete, actionable design or plan, not vague advice."
    ),
    "documentation-expert": (
        "You create and improve documentation for code, architecture, and APIs. "
        "Produce clear, correct, well-structured docs (Markdown) appropriate to the task."
    ),
    "dependency-manager": (
        "You manage software dependencies: updates, conflict resolution, compatibility, and "
        "known security concerns. Produce specific recommendations with reasoning."
    ),
    "devops-experience-architect": (
        "You design environments, CI/CD pipelines, containerization, secrets handling, and "
        "developer tooling. Produce concrete configuration and step-by-step setup guidance."
    ),
    "code-reviewer": (
        "You are an expert code reviewer focused on correctness, maintainability, and security. "
        "Given code or a change description, produce prioritized, specific findings and fixes."
    ),
    "code-cleanup-optimizer": (
        "You reduce technical debt and improve quality AFTER functionality is verified: remove "
        "redundancy, clarify naming, and simplify. Never change behavior. Produce concrete edits."
    ),
    "task-completion-verifier": (
        "You validate that deliverables meet the stated requirements and acceptance criteria, and "
        "that edge cases are handled. Produce a pass/fail judgement per requirement with evidence."
    ),
    # A safe fallback used when the planner does not pick a specific specialist.
    "generalist": (
        "You are a capable generalist engineer. Complete the given phase precisely and concisely, "
        "producing a self-contained deliverable."
    ),
}


def build_specialists(model: str | Model | None = None) -> dict[str, Agent]:
    """Instantiate one ``Agent`` per specialist role, keyed by name.

    ``model`` is applied to every specialist; leave it ``None`` to use the configured default
    provider/model, or pass a concrete/scripted model (e.g. for offline tests).
    """
    return {
        name: Agent(name=name, model=model, instructions=instructions, output_type=str)
        for name, instructions in _SPECIALIST_SPECS.items()
    }


def specialist_catalog() -> str:
    """A short catalog string the planner uses to choose an agent per phase."""
    return "\n".join(
        f"- {name}: {instructions.split('.')[0]}."
        for name, instructions in _SPECIALIST_SPECS.items()
        if name != "generalist"
    )


SPECIALIST_NAMES = tuple(_SPECIALIST_SPECS.keys())
