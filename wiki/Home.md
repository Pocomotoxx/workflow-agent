# Wiki — Agents SDK (provider-agnostic fork)

🇬🇧 English · [🇭🇺 Magyar](Home.hu.md)

Welcome. This wiki documents the fork's own additions and how to keep it independent from upstream.
For the base SDK's deep API reference, use the `docs/` site (built with MkDocs).

## Pages

- **[Installation](../INSTALL.md)** — set up the fork and its tooling.
- **[Providers](Providers.md)** — run against any LLM without an OpenAI key.
- **[Features](Features.md)** — the orchestrator, system factory, and visual designer.
- **[Maintaining the fork](Maintaining-the-Fork.md)** — stay detached from upstream so a sync never
  overwrites your work.

## What this fork is

An independent fork of [openai/openai-agents-python](https://github.com/openai/openai-agents-python)
(MIT, © 2025 OpenAI) that makes "any provider" the default and adds workflow-orchestration,
system-generation, and a visual designer — while keeping the upstream `agents` API intact.

## Publishing this wiki on GitHub

These pages live in the repo under `wiki/` so they are versioned with the code. To also serve them as
the GitHub Wiki: enable **Settings → Features → Wikis**, then either copy these files into the wiki
(the wiki is its own git repo at `github.com/Pocomotoxx/workflow-agent.wiki.git`) or keep browsing
them here in `wiki/`.
