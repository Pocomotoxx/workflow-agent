"""Offline tests for the system-factory web backend. Skipped if FastAPI is not installed."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from examples.system_factory.webapp.backend.app import app  # noqa: E402

client = TestClient(app)

SPEC = {
    "name": "demo_system",
    "description": "A demo.",
    "provider_env": "AGENTS_DEFAULT_PROVIDER",
    "model_env": "AGENTS_DEFAULT_MODEL",
    "required_env": ["TAVILY_API_KEY"],
    "agents": [
        {"name": "researcher", "role": "Analyst", "goal": "Research", "backstory": "", "tools": []},
        {"name": "writer", "role": "Writer", "goal": "Write", "backstory": "", "tools": []},
    ],
    "tasks": [
        {
            "id": "t1",
            "description": "Research.",
            "agent": "researcher",
            "expected_output": "",
            "depends_on": [],
        },
        {
            "id": "t2",
            "description": "Write.",
            "agent": "writer",
            "expected_output": "",
            "depends_on": ["t1"],
        },
    ],
    "mcp_servers": [],
}


def test_list_backends() -> None:
    resp = client.get("/api/backends")
    assert resp.status_code == 200
    assert set(resp.json()["backends"]) == {"crewai", "agents-python"}


def test_validate_ok_and_error() -> None:
    assert client.post("/api/validate", json=SPEC).json() == {"ok": True, "error": None}

    bad = {**SPEC, "tasks": [{"id": "t1", "description": "", "agent": "ghost", "depends_on": []}]}
    body = client.post("/api/validate", json=bad).json()
    assert body["ok"] is False
    assert "unknown agent" in body["error"]


@pytest.mark.parametrize("backend", ["agents-python", "crewai"])
def test_generate(backend: str) -> None:
    resp = client.post("/api/generate", json={"spec": SPEC, "backend": backend})
    assert resp.status_code == 200
    data = resp.json()
    assert data["backend"] == backend
    assert "README.md" in data["files"]
    assert "```mermaid" in data["presentation"]
    # never emit secret values
    assert "sk-" not in data["files"][".env.example"]


def test_generate_rejects_bad_spec() -> None:
    bad = {**SPEC, "tasks": [{"id": "t1", "description": "", "agent": "ghost", "depends_on": []}]}
    resp = client.post("/api/generate", json={"spec": bad, "backend": "crewai"})
    assert resp.status_code == 400
