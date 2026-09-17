# Funkciók

[🇬🇧 English](Features.md) · 🇭🇺 Magyar

Három eszközzel bővül az alap-SDK. Mindegyik providerfüggetlen, és bármelyik operációs rendszeren fut.

## Munkafolyamat-vezénylő

`examples/orchestrator/` — a feladatot szakértő ügynökökre bízza, és függőségi gráfként futtatja.

- A **tervező** ügynök a feladatot atomi fázisokra bontja, mindegyiket egy szakértőhöz rendeli, és
  jelöli a függőségeket (strukturált kimenettel).
- A fázisok **hullámokba** (topológiai szintekbe) rendeződnek; egy hullámban a független fázisok
  **párhuzamosan** futnak (`asyncio.gather`), a hullámok pedig sorban.
- Az **összefésülő** minden fázis kimenetét egy végső válasszá gyúrja össze.

```bash
python examples/orchestrator/orchestrator.py "Készíts indítási tervet egy mobilapphoz"
```

A `run_workflow(task, model=...)` fogad injektált modellt, így teljesen offline is tesztelhető.

## Rendszergyár

`examples/system_factory/` — **metaügynök**, amely a feladatból megtervez egy többügynökös rendszert,
és futtatható projektet generál hozzá.

- Az **architect** ügynök egy keretrendszer-semleges `SystemSpec`-et állít elő (ügynökök, feladatok,
  függőségek, MCP-szerverek, a szükséges környezeti változók nevei).
- **Cserélhető backendek** alakítják a specet projektté: `crewai` (CrewAI-projekt) vagy
  `agents-python` (Agents SDK-projekt).
- A generált Python fordíthatóságát ellenőrzi, és egy Markdown **bemutatót** készít Mermaid-ábrával.

```bash
python -m examples.system_factory.factory "Kutass fel egy piacot és írj összefoglalót" --backend crewai --out generated
```

Biztonság: a titkok sosem tárolódnak — a spec csak a környezeti változók **neveit** hivatkozza. A
`build_system()` sosem futtatja a generált kódot; az éles futtatás külön engedéllyel indul, a
`sandbox.run_generated(..., confirm=True)` hívással.

## Vizuális tervező (webalkalmazás)

`examples/system_factory/webapp/` — böngészőben futó, húzd-és-ejtsd szerkesztő a `SystemSpec`-hez.

- **Frontend**: Vite + React + `@xyflow/react` (React Flow), dagre automatikus elrendezéssel. A
  feladatok a csomópontok (ügynökkel címkézve), a függőségek az élek.
- **Backend**: kis FastAPI-réteg a gyár körül (`/api/validate`, `/api/generate`, `/api/architect`).
  A lefordított SPA-t azonos originről szolgálja ki, ha a `frontend/dist` létezik.

```bash
pip install "fastapi" "uvicorn[standard]"
cd examples/system_factory/webapp/frontend && npm install && npm run build && cd -
uvicorn examples.system_factory.webapp.backend.app:app --port 8000   # http://localhost:8000
```

A vizuális megoldás az AutoGen Studio csapatépítőjének mintájára készült, a mi providerfüggetlen
`SystemSpec`-ünkre újraépítve.
