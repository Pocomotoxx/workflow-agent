"""Offline tests for the orchestrator example's dependency-wave computation.

These exercise pure scheduling logic and make no LLM/provider calls.
"""

from __future__ import annotations

import pytest

from examples.orchestrator.orchestrator import Phase, compute_waves


def _ids(waves: list[list[Phase]]) -> list[set[str]]:
    return [{p.id for p in wave} for wave in waves]


def test_independent_phases_are_one_wave() -> None:
    phases = [
        Phase(id="a", description="", agent="generalist"),
        Phase(id="b", description="", agent="generalist"),
    ]
    assert _ids(compute_waves(phases)) == [{"a", "b"}]


def test_linear_chain_is_sequential_waves() -> None:
    phases = [
        Phase(id="a", description="", agent="generalist"),
        Phase(id="b", description="", agent="generalist", depends_on=["a"]),
        Phase(id="c", description="", agent="generalist", depends_on=["b"]),
    ]
    assert _ids(compute_waves(phases)) == [{"a"}, {"b"}, {"c"}]


def test_diamond_dependency() -> None:
    # a -> b, a -> c, (b,c) -> d
    phases = [
        Phase(id="a", description="", agent="generalist"),
        Phase(id="b", description="", agent="generalist", depends_on=["a"]),
        Phase(id="c", description="", agent="generalist", depends_on=["a"]),
        Phase(id="d", description="", agent="generalist", depends_on=["b", "c"]),
    ]
    assert _ids(compute_waves(phases)) == [{"a"}, {"b", "c"}, {"d"}]


def test_unknown_dependency_raises() -> None:
    phases = [Phase(id="a", description="", agent="generalist", depends_on=["missing"])]
    with pytest.raises(ValueError, match="unknown phase"):
        compute_waves(phases)


def test_cycle_raises() -> None:
    phases = [
        Phase(id="a", description="", agent="generalist", depends_on=["b"]),
        Phase(id="b", description="", agent="generalist", depends_on=["a"]),
    ]
    with pytest.raises(ValueError, match="cycle"):
        compute_waves(phases)


def test_empty_plan() -> None:
    assert compute_waves([]) == []
