# System factory (meta-agent)

Give it a task (plus, optionally, available MCP servers and access notes) and it **designs a
multi-agent system, generates a runnable project for it, validates it, and produces a
presentation** of what it built and how it works. The generated project is provider-agnostic and
runs on any OS.

This builds on the [orchestrator example](../orchestrator/): the orchestrator *runs* a fixed set of
specialists; the factory *designs and generates a new system as code*.

## Pipeline

1. **Architect** — an `Agent` turns the task into a structured `SystemSpec` (agents, tasks,
   dependencies, MCP servers, required env var **names**).
2. **Validate** — referential integrity of the spec (real agents, no unknown/cyclic deps).
3. **Generate** — a pluggable backend renders a runnable project:
   - `crewai` — a CrewAI project (`crew.py`, `requirements.txt`, `.env.example`, `README.md`).
   - `agents-python` — an Agents SDK project (`agent_system.py`, …).
4. **Validate generated code** — every generated `*.py` must compile.
5. **Present** — a static `PRESENTATION.md` with a Mermaid architecture diagram, agents, task flow,
   and run instructions.

## Safety model

- **Secrets are never stored or entered.** The spec and files reference env var *names* only; you
  supply values in your own environment.
- **Static first.** `build_system(...)` never runs the generated system.
- **Live run is opt-in and separate.** `sandbox.run_generated(dir, backend, confirm=True)` runs the
  project as a subprocess only when you explicitly confirm. A subprocess is not true isolation —
  for that, run generated projects in a container / the SDK sandbox extras.

## Use it

```bash
# Design + generate (no LLM key needed for a non-OpenAI provider):
export AGENTS_DEFAULT_PROVIDER=litellm
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=...

python -m examples.system_factory.factory \
  "Research a market and produce a competitive brief" --backend crewai --out generated
```

```python
from examples.system_factory import build_system

project = await build_system("...task...", backend="agents-python")
print(project.presentation_md)
root = project.write_to("generated")  # writes files + PRESENTATION.md
```

`build_system(task, model=...)` accepts an injected model, so the whole pipeline runs fully offline
in tests (see `tests/test_system_factory.py`, which uses a `ScriptedModel`).

## Visual designer (web app)

[`webapp/`](webapp/) is a browser-based, drag-and-drop designer for a `SystemSpec` (React Flow +
dagre, backed by a small FastAPI wrapper around this factory). Build a system as a graph, then
generate a project and view its presentation. Inspired by AutoGen Studio's team builder, but
provider-agnostic and wired to these generators. See [webapp/README.md](webapp/README.md).
