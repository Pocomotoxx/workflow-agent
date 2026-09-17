# Telepítés

[🇬🇧 English](INSTALL.md) · 🇭🇺 Magyar

## Követelmények

- **Python 3.10+**
- **git**
- Csak a vizuális tervezőhöz: **Node.js 18+** és **npm** (vagy pnpm).

## 1. A fork telepítése

A fork osztozik az `openai-agents` csomagnéven az eredetivel, saját néven viszont nem került fel a
PyPI-ra, ezért a repóból telepítsd, ne a PyPI-ról.

**GitHubról (leggyorsabb):**

```bash
pip install "git+https://github.com/Pocomotoxx/agents-python.git"
# a nem-OpenAI providerekkel együtt:
pip install "openai-agents[litellm] @ git+https://github.com/Pocomotoxx/agents-python.git"
```

**Helyi klónból (fejlesztéshez ezt ajánljuk):**

```bash
git clone https://github.com/Pocomotoxx/agents-python.git
cd agents-python
python -m venv .venv
. .venv/bin/activate            # Windowson (PowerShell): .venv\Scripts\Activate.ps1
pip install -e ".[litellm]"
```

### Választható extrák

| Extra | Mit kapcsol be |
| --- | --- |
| `litellm` | 100+ nem-OpenAI provider (Anthropic, Google, Mistral, helyi, …) |
| `voice` | Hang-folyamatok (hozzáadja a `numpy`, `websockets` csomagot) |
| `redis` | Redis-alapú munkamenetek |

Kombinálhatók: `pip install -e ".[litellm,voice,redis]"`.

## 2. Válassz providert (OpenAI-kulcs nélkül)

Két környezeti változóval bármelyik provider alapértelmezetté tehető:

```bash
export AGENTS_DEFAULT_PROVIDER=litellm                       # vagy: any-llm, openai
export AGENTS_DEFAULT_MODEL=anthropic/claude-sonnet-4-20250514
export ANTHROPIC_API_KEY=sk-ant-...                          # a provider saját kulcsa
```

- Az `AGENTS_DEFAULT_PROVIDER` dönti el, ki kezeli a prefix nélküli modellneveket: `openai`
  (alapértelmezés), `litellm`, `any-llm`, vagy egy általad regisztrált prefix a `MultiProvider`-en.
- Az `AGENTS_DEFAULT_MODEL` a modell azonosítója, szó szerint továbbadva.

Az OpenAI-hoz hagyd üresen mindkettőt, és állítsd be az `OPENAI_API_KEY`-t. Bővebben a
[wiki/Providers.hu.md](wiki/Providers.hu.md) oldalon.

## 3. Ellenőrzés

```bash
python -c "import agents; print('agents', agents.__version__)"
```

```python
import asyncio
from agents import Agent, Runner

async def main():
    agent = Agent(name="Assistant", instructions="Egy mondatban válaszolj.")
    print((await Runner.run(agent, "Mi az az ügynök?")).final_output)

asyncio.run(main())
```

## 4. A kiegészítő eszközök futtatása

**Munkafolyamat-vezénylő:**

```bash
python examples/orchestrator/orchestrator.py "Készíts indítási tervet egy mobilapphoz"
```

**Rendszergyár (tervezés és projektgenerálás):**

```bash
python -m examples.system_factory.factory "Kutass fel egy piacot és írj összefoglalót" --backend crewai --out generated
```

**Vizuális tervező (webalkalmazás):**

```bash
pip install "fastapi" "uvicorn[standard]"
cd examples/system_factory/webapp/frontend
npm install
npm run build
cd -
uvicorn examples.system_factory.webapp.backend.app:app --port 8000
# nyisd meg: http://localhost:8000
```

Ha frontend-fejlesztéshez azonnali újratöltés kell, futtasd a backendet a :8000 porton, a frontendben
pedig az `npm run dev` parancsot (a Vite fejlesztői szerver a `/api` hívásokat a backendre irányítja).

## 5. Fejlesztői eszközök

A `Makefile` az elsődleges forrás (a CI is ezt használja). Windowson vagy ott, ahol nincs `make`
vagy `bash`, a `make.ps1` képezi le a gyakori célokat:

```powershell
./make.ps1 sync      # minden extra + fejlesztői függőség telepítése (uv kell hozzá)
./make.ps1 check     # formázás-ellenőrzés + lint + típusellenőrzés + tesztek
./make.ps1 tests
```

## Hibaelhárítás

- **`OPENAI_API_KEY`-hibát kapsz másik providerrel** — az `AGENTS_DEFAULT_PROVIDER`-t nem-OpenAI
  értékre kell állítani *még* az importálás vagy futtatás előtt; a prefix nélküli modellnevek ehhez
  irányítódnak, és az OpenAI-kliens így létre sem jön.
- **A `pip install openai-agents` rossz kódot telepített** — az az eredeti csomagot húzza le. A fork
  funkcióihoz a repóból telepíts (1. lépés).
- **A frontend build elszáll az esbuildnél** — tiszta `npm install` kell; töröld a `node_modules` és
  a `node_modules/.vite` mappát, majd telepítsd újra. A backend a `frontend/dist` mappát szolgálja
  ki, amit a `npm run build` állít elő.
