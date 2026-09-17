# System Factory Designer (web app)

A visual, drag-and-drop workflow designer for the [system factory](../). Build a multi-agent system
as a graph, then generate a runnable project and see its presentation — in the browser.

The design is inspired by AutoGen Studio's team builder (React Flow + dagre auto-layout), but it is
provider-agnostic and produces our framework-neutral `SystemSpec`, feeding the system-factory
generators (CrewAI or Agents SDK) instead of a framework-specific format. Portions are inspired by
[microsoft/autogen](https://github.com/microsoft/autogen) (AutoGen Studio), MIT-licensed.

## Architecture

- **Backend** (`backend/app.py`) — a small FastAPI app wrapping the factory:
  - `GET  /api/backends` — available generator backends.
  - `POST /api/validate` — validate a `SystemSpec`.
  - `POST /api/generate` — generate project files + presentation (deterministic, no LLM/key).
  - `POST /api/architect` — design a `SystemSpec` from a task (LLM; needs a provider).
  - If `frontend/dist` exists, the built SPA is served from the same origin (no CORS in prod).
- **Frontend** (`frontend/`) — Vite + React + TypeScript, using `@xyflow/react` (React Flow) for the
  graph and `dagre` for auto-layout. Nodes are tasks (labeled by agent); edges are dependencies.

## Run it

```bash
# 1. Backend deps (in the repo's environment):
pip install "fastapi" "uvicorn[standard]"

# 2. Frontend: build once, then serve everything from the backend (single origin):
cd examples/system_factory/webapp/frontend
npm install
npm run build
cd -
uvicorn examples.system_factory.webapp.backend.app:app --port 8000
# open http://localhost:8000
```

For frontend development with hot reload, run the Vite dev server (it proxies `/api` to :8000):

```bash
# terminal 1
uvicorn examples.system_factory.webapp.backend.app:app --port 8000
# terminal 2
cd examples/system_factory/webapp/frontend && npm run dev   # http://localhost:5173
```

## Using it

1. Edit the system name, description, agents, and required env var **names** on the left.
2. Add tasks (`+ add`), click a node to edit it, and drag between nodes to add dependencies.
   Use **Auto-layout** to re-run the dagre layout.
3. **Validate**, then **Generate** to see the files and `PRESENTATION.md` on the right.
4. Optionally type a task and **Design (LLM)** to have the architect propose a full spec (needs a
   provider configured, e.g. `AGENTS_DEFAULT_PROVIDER` / `AGENTS_DEFAULT_MODEL`).

Secrets are never entered or stored here: the app deals in env var *names* only.
