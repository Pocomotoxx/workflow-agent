from __future__ import annotations

import asyncio
import os

from agents import Agent, Runner, set_tracing_disabled
from agents.decorators import tool

"""Default to any LLM provider without an OpenAI API key.

By default, ``MultiProvider`` (the provider ``Runner`` uses when none is configured) sends bare
model names such as ``gpt-4.1`` to OpenAI. Two provider-agnostic settings let you point that default
at any provider instead, so the SDK runs out of the box without ``OPENAI_API_KEY``:

- ``AGENTS_DEFAULT_PROVIDER`` selects the provider for bare model names ("openai" (default),
  "litellm", "any-llm", or a prefix registered in a provider_map).
- ``AGENTS_DEFAULT_MODEL`` sets the default model for agents that do not set one. It takes
  precedence over ``OPENAI_DEFAULT_MODEL`` and is passed through verbatim.

Run this example against, e.g., Anthropic via LiteLLM:

    export AGENTS_DEFAULT_PROVIDER=litellm
    export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
    export ANTHROPIC_API_KEY=sk-ant-...
    python examples/model_providers/default_provider.py

Requires the LiteLLM extra: ``pip install 'openai-agents[litellm]'``.
"""

# Tracing uploads to OpenAI by default; disable it since this example assumes no OpenAI credentials.
set_tracing_disabled(disabled=True)

if not os.getenv("AGENTS_DEFAULT_PROVIDER"):
    raise ValueError(
        "Set AGENTS_DEFAULT_PROVIDER (e.g. 'litellm') and AGENTS_DEFAULT_MODEL (e.g. "
        "'anthropic/claude-sonnet-4-20250514') plus the provider's own API key before running."
    )


@tool
def get_weather(city: str) -> str:
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main() -> None:
    # Note: no ``model=`` is set on the Agent, so it uses AGENTS_DEFAULT_MODEL, routed through the
    # provider named by AGENTS_DEFAULT_PROVIDER. No OpenAI client is ever constructed.
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
