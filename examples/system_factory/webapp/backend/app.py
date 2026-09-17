"""FastAPI backend that exposes the system-factory over HTTP for the visual designer.

Endpoints:
- ``GET  /api/backends``  -> available generator backends.
- ``POST /api/validate``  -> validate a SystemSpec (referential integrity).
- ``POST /api/generate``  -> generate project files + presentation from a SystemSpec (no LLM).
- ``POST /api/architect`` -> design a SystemSpec from a natural-language task (needs a provider).

The generate/validate paths are deterministic and need no API key, so the visual designer works
fully offline for editing + code generation. Only ``/api/architect`` calls an LLM.

Run:
    pip install "fastapi" "uvicorn[standard]"
    uvicorn examples.system_factory.webapp.backend.app:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from examples.system_factory.demo import presentation
from examples.system_factory.generators import BACKENDS, get_backend
from examples.system_factory.spec import SystemSpec
from examples.system_factory.validate import SpecValidationError, validate_spec

app = FastAPI(title="System Factory Designer API")

# The Vite dev server runs on a different origin; allow it during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    spec: SystemSpec
    backend: str = "agents-python"


class GenerateResponse(BaseModel):
    files: dict[str, str]
    presentation: str
    backend: str


class ArchitectRequest(BaseModel):
    task: str
    backend: str = "agents-python"
    mcp_hint: str = ""


@app.get("/api/backends")
def list_backends() -> dict[str, list[str]]:
    return {"backends": sorted(BACKENDS)}


@app.post("/api/validate")
def validate(spec: SystemSpec) -> dict[str, object]:
    try:
        validate_spec(spec)
    except SpecValidationError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "error": None}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    try:
        validate_spec(req.spec)
        backend = get_backend(req.backend)
    except (SpecValidationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    files = backend.generate(req.spec)
    return GenerateResponse(
        files=files,
        presentation=presentation(req.spec, backend.name, files),
        backend=backend.name,
    )


@app.post("/api/architect", response_model=SystemSpec)
async def architect(req: ArchitectRequest) -> SystemSpec:
    # Imported lazily so the deterministic endpoints work even if the model layer errors out.
    from examples.system_factory import build_system

    try:
        project = await build_system(req.task, backend=req.backend, mcp_hint=req.mcp_hint)
    except Exception as exc:  # surface provider/config errors to the client cleanly
        raise HTTPException(status_code=502, detail=f"Architect failed: {exc}") from exc
    return project.spec


# If the frontend has been built (frontend/dist), serve it from this same server so the SPA and API
# share one origin (no CORS needed in production). Mounted last so /api/* routes still take priority.
_DIST = Path(__file__).resolve().parents[1] / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="frontend")
