# Installation

🇬🇧 English · [🇭🇺 Magyar](INSTALL.hu.md)

## Requirements

- **Python 3.10+**
- **git**
- For the visual designer only: **Node.js 18+** and **npm** (or pnpm).

## 1. Install the fork

Because this fork shares the package name `openai-agents` with upstream but is not published to PyPI
under its own name, install it from the repository — not from PyPI.

**From GitHub (quickest):**

```bash
pip install "git+https://github.com/Pocomotoxx/workflow-agent.git"
# with non-OpenAI providers enabled:
pip install "openai-agents[litellm] @ git+https://github.com/Pocomotoxx/workflow-agent.git"
```

**From a local clone (recommended for development):**

```bash
git clone https://github.com/Pocomotoxx/workflow-agent.git
cd agents-python
python -m venv .venv
. .venv/bin/activate            # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -e ".[litellm]"
```

### Optional extras

| Extra | Enables |
| --- | --- |
| `litellm` | 100+ non-OpenAI providers (Anthropic, Google, Mistral, local, …) |
| `voice` | Voice pipelines (adds `numpy`, `websockets`) |
| `redis` | Redis-backed sessions |

Combine them: `pip install -e ".[litellm,voice,redis]"`.

## 2. Choose a provider (no OpenAI key needed)

Set two environment variables to make any provider the default:

```bash
export AGENTS_DEFAULT_PROVIDER=litellm                       # or: any-llm, openai
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...                          # your provider's own key
```

- `AGENTS_DEFAULT_PROVIDER` picks who handles bare model names: `openai` (default), `litellm`,
  `any-llm`, or a prefix you register on a `MultiProvider`.
- `AGENTS_DEFAULT_MODEL` is the default model id, passed through verbatim.

To use OpenAI, leave both unset and set `OPENAI_API_KEY`. See [wiki/Providers.md](wiki/Providers.md).

## 3. Verify

```bash
python -c "import agents; print('agents', agents.__version__)"
```

```python
import asyncio
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="Answer in one sentence.")
    print((await Runner.run(agent, "What is an agent?")).final_output)

asyncio.run(main())
```

## 4. Run the added tooling

**Workflow orchestrator:**

```bash
python examples/orchestrator/orchestrator.py "Draft a launch plan for a mobile app"
```

**System factory (design + generate a project):**

```bash
python -m examples.system_factory.factory "Research a market and write a brief" --backend crewai --out generated
```

**Visual designer (web app):**

```bash
pip install "fastapi" "uvicorn[standard]"
cd examples/system_factory/webapp/frontend
npm install
npm run build
cd -
uvicorn examples.system_factory.webapp.backend.app:app --port 8000
# open http://localhost:8000
```

For hot-reload frontend development, run the backend on :8000 and `npm run dev` in the frontend
(the Vite dev server proxies `/api` to the backend).

## 5. Development tooling

The `Makefile` is the source of truth (used by CI). On Windows or anywhere `make`/`bash` is missing,
`make.ps1` mirrors the common targets:

```powershell
./make.ps1 sync      # install all extras + dev deps (needs uv)
./make.ps1 check     # format-check + lint + typecheck + tests
./make.ps1 tests
```

## Troubleshooting

- **`OPENAI_API_KEY` error with another provider** — make sure `AGENTS_DEFAULT_PROVIDER` is set to a
  non-OpenAI value *before* importing/running; bare model names route to it and the OpenAI client is
  then never constructed.
- **`pip install openai-agents` installed the wrong code** — that pulls the upstream package. Install
  from this repository (step 1) to get the fork's features.
- **Frontend build fails on esbuild** — ensure a clean `npm install`; delete `node_modules` and
  `node_modules/.vite` and reinstall. The production build (`npm run build`) is what the backend
  serves from `frontend/dist`.
