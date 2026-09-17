# Features

🇬🇧 English · [🇭🇺 Magyar](Features.hu.md)

Three tools this fork adds on top of the base SDK. All are provider-agnostic and run on any OS.

## Workflow orchestrator

`examples/orchestrator/` — delegate a task to specialist agents and run it as a dependency graph.

- A **planner** agent decomposes the task into atomic phases, each assigned to a specialist and
  annotated with dependencies (structured output).
- Phases are grouped into **waves** (topological levels); independent phases in a wave run in
  **parallel** (`asyncio.gather`), waves run in order.
- A **consolidator** merges all phase outputs into the final answer.

```bash
python examples/orchestrator/orchestrator.py "Draft a launch plan for a mobile app"
```

`run_workflow(task, model=...)` accepts an injected model, so it is testable fully offline.

## System factory

`examples/system_factory/` — a **meta-agent** that designs a multi-agent system from a task and
generates a runnable project for it.

- **Architect** agent → a framework-neutral `SystemSpec` (agents, tasks, dependencies, MCP servers,
  required env-var names).
- **Pluggable backends** turn the spec into a project: `crewai` (a CrewAI project) or `agents-python`
  (an Agents SDK project).
- Generated Python is compile-checked; a Markdown **presentation** with a Mermaid diagram is produced.

```bash
python -m examples.system_factory.factory "Research a market and write a brief" --backend crewai --out generated
```

Safety: secrets are never stored — the spec references env-var **names** only. `build_system()` never
runs generated code; a live run is opt-in via `sandbox.run_generated(..., confirm=True)`.

## Visual designer (web app)

`examples/system_factory/webapp/` — a browser-based, drag-and-drop editor for a `SystemSpec`.

- **Frontend**: Vite + React + `@xyflow/react` (React Flow) with dagre auto-layout. Tasks are nodes
  (labeled by agent); dependencies are edges.
- **Backend**: a small FastAPI wrapper around the factory (`/api/validate`, `/api/generate`,
  `/api/architect`). It serves the built SPA from the same origin when `frontend/dist` exists.

```bash
pip install "fastapi" "uvicorn[standard]"
cd examples/system_factory/webapp/frontend && npm install && npm run build && cd -
uvicorn examples.system_factory.webapp.backend.app:app --port 8000   # http://localhost:8000
```

The visual pattern is inspired by AutoGen Studio's team builder, reimplemented over our
provider-agnostic `SystemSpec`.
