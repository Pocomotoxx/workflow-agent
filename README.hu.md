# Agents SDK — providerfüggetlen fork

[![PyPI](https://img.shields.io/pypi/v/openai-agents?label=upstream%20pypi)](https://pypi.org/project/openai-agents/)
&nbsp;·&nbsp; [🇬🇧 English](README.md) &nbsp;·&nbsp; 🇭🇺 Magyar

Könnyű, mégis erős keretrendszer többügynökös munkafolyamatokhoz — **alapból providerfüggetlen**.
Bármelyik nyelvi modellre ráállítható (OpenAI, Anthropic, Google, helyi modellek a LiteLLM vagy az
any-llm rétegen át, illetve bármilyen OpenAI-kompatibilis végpont), OpenAI-kulcs nélkül is, és
ügynökrendszereket vezényelhetsz, generálhatsz és vizuálisan tervezhetsz vele bármelyik operációs
rendszeren.

> **Önálló fork ez**, a [openai/openai-agents-python](https://github.com/openai/openai-agents-python)
> forkja (MIT, © 2025 OpenAI). Megőrzi a teljes kompatibilitást az eredeti `agents` API-val, és
> hozzáad egy providerfüggetlen alapértelmezést, munkafolyamat-vezénylést, rendszergenerálást és egy
> vizuális tervezőt. A leválasztás módját a [Fork karbantartása](wiki/Maintaining-the-Fork.hu.md)
> oldal írja le.

## Miért készült ez a fork

Az eredeti SDK már tud több providert kezelni, mindenütt az OpenAI-t választja alapból, és a
kezdéshez `OPENAI_API_KEY` kell. Itt a „bármelyik provider" lett az elsődleges alapérték, és fölé
került néhány magasabb szintű eszköz:

- **Providerfüggetlen alapértékek** — az `AGENTS_DEFAULT_PROVIDER` és az `AGENTS_DEFAULT_MODEL`
  választja ki a providert és a modellt a prefix nélküli modellnevekhez, így az SDK OpenAI-kulcs
  nélkül, azonnal elindul.
- **Munkafolyamat-vezénylő** ([`examples/orchestrator`](examples/orchestrator/)) — a feladatot
  fázisokra bontja, a független fázisokat párhuzamosan futtatja (függőségi „hullámokban"), majd
  összefésüli az eredményeket.
- **Rendszergyár** ([`examples/system_factory`](examples/system_factory/)) — metaügynök, amely a
  feladatból megtervez egy többügynökös rendszert, és **futtatható projektet generál** hozzá (CrewAI
  vagy Agents SDK backenddel), a végén pedig bemutatót készít arról, mit épített.
- **Vizuális tervező** ([`examples/system_factory/webapp`](examples/system_factory/webapp/)) —
  böngészőben futó, húzd-és-ejtsd szerkesztő (React Flow és FastAPI) a rendszerek megtervezéséhez és
  a kód legenerálásához.
- **Platformfüggetlen eszközök** — a `make.ps1` a gyakori `Makefile`-célokat képezi le Windowsra,
  macOS-re és Linuxra.

Minden itt marad, amit az eredeti SDK nyújt: ügynökök, átadások (handoff), eszközök, védőkorlátok,
munkamenetek, nyomkövetés, MCP, valós idejű és hangügynökök, valamint a sandbox futtatókörnyezet.

## Telepítés

A fork saját néven nem került fel a PyPI-ra, ezért **ebből a repóból** telepítsd (a sima
`pip install openai-agents` az eredeti csomagot hozná le helyette):

```bash
pip install "git+https://github.com/Pocomotoxx/workflow-agent.git"
```

Helyi klónból (fejlesztéshez ezt ajánljuk):

```bash
git clone https://github.com/Pocomotoxx/workflow-agent.git
cd agents-python
python -m venv .venv && . .venv/bin/activate      # Windowson: .venv\Scripts\activate
pip install -e ".[litellm]"                        # a 'litellm' extra hozza a nem-OpenAI providereket
```

A részletek — az extrák, a webalkalmazás és a hibaelhárítás — az [INSTALL.hu.md](INSTALL.hu.md)
fájlban vannak.

## Gyors kezdés (OpenAI-kulcs nélkül)

```bash
export AGENTS_DEFAULT_PROVIDER=litellm
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...
```

```python
import asyncio
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="Légy tömör és segítőkész.")
    result = await Runner.run(agent, "Mondj három felhasználást egy gemkapocsra.")
    print(result.final_output)

asyncio.run(main())
```

Nem-OpenAI provider beállításakor az OpenAI-kliens létre sem jön, `OPENAI_API_KEY` sem kell hozzá.
Ha inkább az OpenAI-t használnád, hagyd üresen a két környezeti változót, és állítsd be az
`OPENAI_API_KEY`-t.

## Dokumentáció

- [INSTALL.hu.md](INSTALL.hu.md) — telepítés és beállítás (magyar) · [INSTALL.md](INSTALL.md) (English)
- **Wiki** ([`wiki/`](wiki/)) — [Kezdőlap](wiki/Home.hu.md) · [Providerek](wiki/Providers.hu.md) ·
  [Funkciók](wiki/Features.hu.md) · [Fork karbantartása](wiki/Maintaining-the-Fork.hu.md)
- Az eredeti kézikönyv (a részletes API-leírás): a `docs/` oldal, MkDocs-szal építve.

## Licenc és forrásmegjelölés

MIT. A projekt a [openai/openai-agents-python](https://github.com/openai/openai-agents-python)
forkja; az eredeti szerzői jogi megjelölést (© 2025 OpenAI) a [LICENSE](LICENSE) megtartja, ahogy az
MIT-licenc megköveteli. A forkhoz készült kiegészítések a szerzőik jogai alatt, ugyanezen MIT
feltételekkel érhetők el.
