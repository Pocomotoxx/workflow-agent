# Workflow orchestrator (provider-agnostic)

A proof-of-concept that ports the **ideas** of the Claude Code
[workflow-orchestration plugin](https://github.com/Pocomotoxx/claude-code-workflow-orchestration)
onto the Agents SDK, so the same delegation-based workflow runs against **any** provider and on any
OS — with no Claude Code hooks, plugin manifest, or runtime.

## Why this is a reimplementation, not a port of files

The Claude Code plugin is configuration (agent markdown, `plugin.json`, and `PreToolUse`/`Stop`
hooks) that steers the Claude Code CLI. It makes no model calls itself and only runs inside Claude
Code. This example instead expresses the workflow as ordinary SDK code:

| Plugin concept (Claude Code)        | Here (Agents SDK)                                  |
| ----------------------------------- | -------------------------------------------------- |
| Specialist agents (`agents/*.md`)   | `Agent` objects in `specialists.py`                |
| Plan mode + decomposition           | A planner `Agent` with structured (`Plan`) output  |
| Wave / dependency scheduling        | `compute_waves()` (topological levels)             |
| Parallel wave execution             | `asyncio.gather` over a wave                        |
| Delegation-enforcement hooks        | Not needed — control flow is just code             |
| Task tracking (TaskCreate/…)        | The `results` dict passed between phases            |

## Pipeline

1. **Plan** — the planner decomposes the task into atomic phases, each assigned to a specialist and
   annotated with dependencies (structured output).
2. **Waves** — phases are grouped into dependency waves (topological levels).
3. **Execute** — phases in a wave run in parallel; waves run in order; each phase receives its
   dependencies' outputs as context.
4. **Consolidate** — a consolidator agent merges all phase artifacts into the final answer.

## Run it

Defaults to OpenAI. To use any other provider without an OpenAI key, set the provider-agnostic
defaults (see [../model_providers/](../model_providers/)):

```bash
export AGENTS_DEFAULT_PROVIDER=litellm
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=...
python examples/orchestrator/orchestrator.py "Add rate limiting to our public API"
```

`run_workflow(task, model=...)` accepts an injected model, so the pipeline can be driven fully
offline in tests (see `tests/test_orchestrator_e2e.py`, which uses a `ScriptedModel`).
