# Agents SDK — provider-agnostic fork

[![PyPI](https://img.shields.io/pypi/v/openai-agents?label=upstream%20pypi)](https://pypi.org/project/openai-agents/)
&nbsp;·&nbsp; 🇬🇧 English &nbsp;·&nbsp; [🇭🇺 Magyar](README.hu.md)

A lightweight yet powerful framework for building multi-agent workflows — **provider-agnostic by
default**. Point it at any LLM (OpenAI, Anthropic, Google, local models via LiteLLM / any-llm, or an
OpenAI-compatible endpoint) without an OpenAI API key, and orchestrate, generate, and visually
design agent systems on any OS.

> **This is an independent fork** of [openai/openai-agents-python](https://github.com/openai/openai-agents-python)
> (MIT, © 2025 OpenAI). It keeps full compatibility with the upstream `agents` API and adds a
> provider-agnostic default plus workflow-orchestration, system-generation, and a visual designer.
> See [Maintaining the fork](wiki/Maintaining-the-Fork.md) for how it stays detached from upstream.

## Why this fork

The upstream SDK is already provider-capable, but it defaults to OpenAI everywhere and needs an
`OPENAI_API_KEY` to get started. This fork makes "any provider" the first-class default and layers
higher-level tooling on top:

- **Provider-agnostic defaults** — `AGENTS_DEFAULT_PROVIDER` and `AGENTS_DEFAULT_MODEL` select the
  provider and model for bare model names, so the SDK runs out of the box with no OpenAI credentials.
- **Workflow orchestrator** ([`examples/orchestrator`](examples/orchestrator/)) — decompose a task
  into phases, run independent phases in parallel (dependency "waves"), and consolidate the results.
- **System factory** ([`examples/system_factory`](examples/system_factory/)) — a meta-agent that
  designs a multi-agent system from a task and **generates a runnable project** for it (CrewAI or
  Agents SDK backends), plus a presentation of what it built.
- **Visual designer** ([`examples/system_factory/webapp`](examples/system_factory/webapp/)) — a
  browser-based, drag-and-drop editor (React Flow + FastAPI) for designing systems and generating
  code.
- **Cross-platform tooling** — `make.ps1` mirrors the common `Makefile` targets for Windows/macOS/Linux.

Everything the upstream SDK offers is still here: agents, handoffs, tools, guardrails, sessions,
tracing, MCP, realtime and voice agents, and the sandbox runtime.

## Install

This fork is not published to PyPI under its own name, so install it **from this repository** (a
plain `pip install openai-agents` would fetch the upstream package instead):

```bash
pip install "git+https://github.com/Pocomotoxx/agents-python.git"
```

Or from a local clone (recommended for development):

```bash
git clone https://github.com/Pocomotoxx/agents-python.git
cd agents-python
python -m venv .venv && . .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[litellm]"                        # 'litellm' extra enables non-OpenAI providers
```

Full details — extras, the web app, and troubleshooting — are in [INSTALL.md](INSTALL.md).

## Quick start (no OpenAI key)

```bash
export AGENTS_DEFAULT_PROVIDER=litellm
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
import asyncio
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="You are concise and helpful.")
    result = await Runner.run(agent, "Name three uses for a paperclip.")
    print(result.final_output)

asyncio.run(main())
```

Because a non-OpenAI provider is configured, the OpenAI client is never constructed and no
`OPENAI_API_KEY` is required. To use OpenAI instead, leave the two env vars unset and set
`OPENAI_API_KEY`.

## Documentation

- [INSTALL.md](INSTALL.md) — installation and setup (English) · [INSTALL.hu.md](INSTALL.hu.md) (magyar)
- **Wiki** ([`wiki/`](wiki/)) — [Home](wiki/Home.md) · [Providers](wiki/Providers.md) ·
  [Features](wiki/Features.md) · [Maintaining the fork](wiki/Maintaining-the-Fork.md)
- Upstream reference docs (the deep API manual): the `docs/` site, built with MkDocs.

## License & attribution

MIT. This project is a fork of [openai/openai-agents-python](https://github.com/openai/openai-agents-python);
the original copyright (© 2025 OpenAI) is retained in [LICENSE](LICENSE) as required by the MIT
license. Fork-specific additions are © their respective authors under the same MIT terms.
