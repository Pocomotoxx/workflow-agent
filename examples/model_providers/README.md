# Model provider examples

The examples in this directory show how to route models through adapter layers such as LiteLLM and
any-llm. The default examples all use OpenRouter so you only need one API key:

```bash
export OPENROUTER_API_KEY="..."
```

Run one of the adapter examples:

```bash
uv run examples/model_providers/any_llm_provider.py
uv run examples/model_providers/any_llm_auto.py
uv run examples/model_providers/litellm_provider.py
uv run examples/model_providers/litellm_auto.py
```

Direct-model examples let you override the target model:

```bash
uv run examples/model_providers/any_llm_provider.py --model openrouter/openai/gpt-5.4-mini
uv run examples/model_providers/litellm_provider.py --model openrouter/openai/gpt-5.4-mini
```

## Default to a non-OpenAI provider (no OpenAI API key)

`default_provider.py` shows how to make the SDK default to any provider — so bare/unset model names
never touch OpenAI — using the provider-agnostic `AGENTS_DEFAULT_PROVIDER` and `AGENTS_DEFAULT_MODEL`
settings. No `OPENAI_API_KEY` required:

```bash
export AGENTS_DEFAULT_PROVIDER=litellm
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY="..."
uv run examples/model_providers/default_provider.py
```
