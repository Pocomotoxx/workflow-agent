# Providers

🇬🇧 English · [🇭🇺 Magyar](Providers.hu.md)

The fork makes any LLM provider a first-class default. There are three levels of control.

## 1. Global default (env vars)

```bash
export AGENTS_DEFAULT_PROVIDER=litellm      # openai (default) | litellm | any-llm | a provider_map prefix
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...
```

- Bare model names (e.g. `gpt-4.1`) and unset agent models route to `AGENTS_DEFAULT_PROVIDER`.
- When it is not `openai`, the OpenAI client is never constructed — **no `OPENAI_API_KEY` required**.
- `AGENTS_DEFAULT_MODEL` takes precedence over `OPENAI_DEFAULT_MODEL` and is passed through verbatim
  (so case-sensitive model ids survive).

## 2. Per run (`MultiProvider`)

```python
from agents import Agent, MultiProvider, RunConfig, Runner

provider = MultiProvider(default_provider="litellm")
agent = Agent(name="Assistant", instructions="Be helpful.")
result = await Runner.run(
    agent, "Hello!",
    run_config=RunConfig(model_provider=provider, model="anthropic/claude-sonnet-4-20250514"),
)
```

Explicit prefixes always win, so you can mix providers in one run: `openai/gpt-4.1`,
`litellm/anthropic/claude-...`, `any-llm/openrouter/...`.

## 3. Per agent (explicit model or client)

```python
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

set_tracing_disabled(True)  # tracing uploads to OpenAI by default
client = AsyncOpenAI(base_url="https://your-openai-compatible-endpoint/v1", api_key="...")
agent = Agent(
    name="Assistant",
    model=OpenAIChatCompletionsModel(model="your-model", openai_client=client),
)
```

## Notes

- Install the `litellm` extra for non-OpenAI providers: `pip install -e ".[litellm]"`.
- Tracing uploads to OpenAI by default; when you have no OpenAI key, call `set_tracing_disabled(True)`
  or configure a different tracing processor.
- To use OpenAI, leave the two env vars unset and set `OPENAI_API_KEY`.
