"""Offline end-to-end test of the orchestrator example using a ScriptedModel.

Proves the full plan -> waves -> execute -> consolidate pipeline wires up, with no provider calls.
A linear plan (one phase per wave) keeps scripted-step consumption order deterministic.
"""

from __future__ import annotations

import json

import pytest

from agents.testing.model import ScriptedModel
from examples.orchestrator.orchestrator import run_workflow
from tests.test_responses import get_text_message

PLAN = {
    "reasoning": "Design, document, then verify.",
    "phases": [
        {
            "id": "p1",
            "description": "Design the approach.",
            "agent": "tech-lead-architect",
            "depends_on": [],
        },
        {
            "id": "p2",
            "description": "Document the design.",
            "agent": "documentation-expert",
            "depends_on": ["p1"],
        },
        {
            "id": "p3",
            "description": "Verify the deliverables.",
            "agent": "task-completion-verifier",
            "depends_on": ["p2"],
        },
    ],
}


@pytest.mark.asyncio
async def test_orchestrator_pipeline_offline() -> None:
    model = ScriptedModel(
        [
            [get_text_message(json.dumps(PLAN))],  # planner -> structured Plan
            [get_text_message("DESIGN: use a token bucket.")],  # p1
            [get_text_message("DOCS: token-bucket rate limiter.")],  # p2
            [get_text_message("VERIFIED: all requirements met.")],  # p3
            [get_text_message("FINAL: rate limiting designed, documented, and verified.")],
        ]
    )

    result = await run_workflow("Add rate limiting to our public API", model=model)

    assert "FINAL" in result
    # Planner + 3 phases + consolidator = 5 model calls, all consumed.
    assert len(model.calls) == 5
    model.assert_complete()
    # The consolidator's input must include every phase's artifact.
    consolidator_input = str(model.calls[-1].input)
    assert "DESIGN" in consolidator_input
    assert "DOCS" in consolidator_input
    assert "VERIFIED" in consolidator_input
