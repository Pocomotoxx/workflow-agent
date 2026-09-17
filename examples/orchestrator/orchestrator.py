"""Provider-agnostic workflow orchestrator (proof of concept).

This example ports the *ideas* of the Claude Code "workflow orchestration" plugin
(https://github.com/Pocomotoxx/claude-code-workflow-orchestration) onto the Agents SDK, so the same
delegation-based workflow runs against **any** provider and on any OS — without Claude Code's hooks,
plugin manifest, or runtime.

Pipeline:
  Stage 0 - Plan:    a planner Agent decomposes the task into atomic phases, each assigned to a
                     specialist and annotated with dependencies (structured output).
  Waves:             phases are grouped into dependency "waves" (topological levels).
  Stage 1 - Execute: phases in a wave run in parallel (asyncio.gather); waves run in order.
                     Each phase receives the outputs of its dependencies as context.
  Stage 2 - Consolidate: a consolidator Agent summarizes all phase artifacts into a final answer.

Run it (defaults to OpenAI; set the env vars below to use any other provider without an OpenAI key):

    # e.g. Anthropic via LiteLLM -- needs `pip install 'openai-agents[litellm]'`
    export AGENTS_DEFAULT_PROVIDER=litellm
    export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/orchestrator/orchestrator.py "Add rate limiting to our public API"
"""

from __future__ import annotations

import asyncio
import sys

from pydantic import BaseModel, Field

from agents import Agent, Runner, set_tracing_disabled, trace
from agents.models.interface import Model

try:
    # When imported as a package: `python -m examples.orchestrator.orchestrator`.
    from .specialists import SPECIALIST_NAMES, build_specialists, specialist_catalog
except ImportError:
    # When run as a script: `python examples/orchestrator/orchestrator.py`.
    from specialists import SPECIALIST_NAMES, build_specialists, specialist_catalog  # type: ignore

# Tracing uploads to OpenAI by default; disable it so this example is fully provider-agnostic and
# needs no OpenAI credentials. Remove this if you have an OpenAI key and want traces.
set_tracing_disabled(disabled=True)


# ---- Stage 0: planning schema -------------------------------------------------------------------


class Phase(BaseModel):
    id: str = Field(description="Short unique id for this phase, e.g. 'p1'.")
    description: str = Field(description="Self-contained instruction for the specialist.")
    agent: str = Field(description=f"One of: {', '.join(SPECIALIST_NAMES)}.")
    depends_on: list[str] = Field(
        default_factory=list,
        description="Ids of phases that must finish before this one. Empty if independent.",
    )


class Plan(BaseModel):
    reasoning: str = Field(description="Brief rationale for the decomposition.")
    phases: list[Phase]


def _build_planner(model: str | Model | None = None) -> Agent:
    return Agent(
        name="orchestrator-planner",
        model=model,
        instructions=(
            "You are a workflow orchestrator. Decompose the user's task into a minimal set of "
            "atomic phases. Assign each phase to the most appropriate specialist and declare its "
            "dependencies via `depends_on` (referencing earlier phase ids). Make independent "
            "phases have no shared dependencies so they can run in parallel. Prefer 2-6 phases. "
            "End with a verification phase assigned to 'task-completion-verifier' that depends on "
            "the phases producing deliverables.\n\nAvailable specialists:\n" + specialist_catalog()
        ),
        output_type=Plan,
    )


def _build_consolidator(model: str | Model | None = None) -> Agent:
    return Agent(
        name="orchestrator-consolidator",
        model=model,
        instructions=(
            "You consolidate the outputs of several specialist phases into one coherent final "
            "answer for the user. Integrate the artifacts, resolve overlaps, and present a clear, "
            "actionable result. Do not invent work that was not done."
        ),
        output_type=str,
    )


# ---- Wave computation ---------------------------------------------------------------------------


def compute_waves(phases: list[Phase]) -> list[list[Phase]]:
    """Group phases into dependency waves (topological levels). Raises on unknown deps or cycles."""
    by_id = {p.id: p for p in phases}
    for p in phases:
        for dep in p.depends_on:
            if dep not in by_id:
                raise ValueError(f"Phase {p.id!r} depends on unknown phase {dep!r}.")

    level: dict[str, int] = {}

    def resolve(pid: str, stack: frozenset[str]) -> int:
        if pid in level:
            return level[pid]
        if pid in stack:
            raise ValueError(f"Dependency cycle detected involving phase {pid!r}.")
        deps = by_id[pid].depends_on
        lvl = 0 if not deps else 1 + max(resolve(d, stack | {pid}) for d in deps)
        level[pid] = lvl
        return lvl

    for p in phases:
        resolve(p.id, frozenset())

    max_level = max(level.values(), default=-1)
    waves: list[list[Phase]] = [[] for _ in range(max_level + 1)]
    for p in phases:
        waves[level[p.id]].append(p)
    return waves


# ---- Stage 1: execution -------------------------------------------------------------------------


async def _run_phase(
    phase: Phase,
    specialists: dict[str, Agent],
    results: dict[str, str],
) -> tuple[str, str]:
    agent = specialists.get(phase.agent) or specialists["generalist"]
    context_blocks = [
        f"### Result of dependency '{dep}':\n{results[dep]}"
        for dep in phase.depends_on
        if dep in results
    ]
    prompt = phase.description
    if context_blocks:
        prompt += "\n\n---\nUse these upstream results as context:\n\n" + "\n\n".join(
            context_blocks
        )
    run_result = await Runner.run(agent, prompt)
    return phase.id, str(run_result.final_output)


async def run_workflow(task: str, *, model: str | Model | None = None) -> str:
    """Run the full plan -> waves -> execute -> consolidate pipeline.

    ``model`` is applied to every agent; pass a ``ScriptedModel`` to run fully offline in tests, or
    leave it ``None`` to use the configured default provider.
    """
    specialists = build_specialists(model=model)
    planner = _build_planner(model)
    consolidator = _build_consolidator(model)

    with trace("Workflow orchestration"):
        plan_result = await Runner.run(planner, task)
        plan = plan_result.final_output
        assert isinstance(plan, Plan)

        waves = compute_waves(plan.phases)
        print(f"Planned {len(plan.phases)} phase(s) across {len(waves)} wave(s).")
        print(f"Rationale: {plan.reasoning}\n")

        results: dict[str, str] = {}
        for i, wave in enumerate(waves):
            names = ", ".join(f"{p.id}:{p.agent}" for p in wave)
            print(f"Wave {i} ({len(wave)} phase(s) in parallel): {names}")
            wave_outputs = await asyncio.gather(
                *(_run_phase(p, specialists, results) for p in wave)
            )
            results.update(dict(wave_outputs))

        consolidation_input = f"Original task: {task}\n\n" + "\n\n".join(
            f"## Phase {pid}\n{output}" for pid, output in results.items()
        )
        final = await Runner.run(consolidator, consolidation_input)
        return str(final.final_output)


async def main() -> None:
    task = (
        " ".join(sys.argv[1:]).strip() or "Write a short design note for a URL-shortener service."
    )
    print(f"Task: {task}\n")
    final_output = await run_workflow(task)
    print("\n===== FINAL OUTPUT =====\n")
    print(final_output)


if __name__ == "__main__":
    asyncio.run(main())
