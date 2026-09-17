# Providerek

[🇬🇧 English](Providers.md) · 🇭🇺 Magyar

A fork bármelyik nyelvimodell-providert elsőrangú alapértékké teszi. Három szinten szabályozható.

## 1. Globális alapérték (környezeti változók)

```bash
export AGENTS_DEFAULT_PROVIDER=litellm      # openai (alapértelmezés) | litellm | any-llm | egy provider_map prefix
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...
```

- A prefix nélküli modellnevek (például `gpt-4.1`) és a be nem állított ügynökmodellek az
  `AGENTS_DEFAULT_PROVIDER`-hez irányítódnak.
- Ha ez nem `openai`, az OpenAI-kliens létre sem jön — **`OPENAI_API_KEY` sem kell**.
- Az `AGENTS_DEFAULT_MODEL` elsőbbséget élvez az `OPENAI_DEFAULT_MODEL`-lel szemben, és szó szerint
  adódik tovább (így a kis-nagybetűre érzékeny modellazonosítók megmaradnak).

## 2. Futásonként (`MultiProvider`)

```python
from agents import Agent, MultiProvider, RunConfig, Runner

provider = MultiProvider(default_provider="litellm")
agent = Agent(name="Assistant", instructions="Légy segítőkész.")
result = await Runner.run(
    agent, "Szia!",
    run_config=RunConfig(model_provider=provider, model="anthropic/claude-sonnet-4-20250514"),
)
```

Az explicit prefixek mindig nyernek, így egy futáson belül keverhetők a providerek:
`openai/gpt-4.1`, `litellm/anthropic/claude-...`, `any-llm/openrouter/...`.

## 3. Ügynökönként (explicit modell vagy kliens)

```python
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

set_tracing_disabled(True)  # a nyomkövetés alapból az OpenAI-ba tölt fel
client = AsyncOpenAI(base_url="https://az-openai-kompatibilis-vegpontod/v1", api_key="...")
agent = Agent(
    name="Assistant",
    model=OpenAIChatCompletionsModel(model="a-modelled", openai_client=client),
)
```

## Megjegyzések

- A nem-OpenAI providerekhez telepítsd a `litellm` extrát: `pip install -e ".[litellm]"`.
- A nyomkövetés alapból az OpenAI-ba tölt fel; OpenAI-kulcs híján hívd meg a
  `set_tracing_disabled(True)`-t, vagy állíts be másik nyomkövetőt.
- Az OpenAI-hoz hagyd üresen a két környezeti változót, és állítsd be az `OPENAI_API_KEY`-t.
