"""Tests for the provider-agnostic default provider/model configuration.

These cover the ability to make the SDK default to any LLM provider (not just OpenAI) via the
``default_provider`` argument / ``AGENTS_DEFAULT_PROVIDER`` env var and the ``AGENTS_DEFAULT_MODEL``
env var, without requiring an OpenAI API key.
"""

from __future__ import annotations

import pytest

from agents import UserError
from agents.models.default_models import get_default_model
from agents.models.interface import Model, ModelProvider
from agents.models.multi_provider import MultiProvider, MultiProviderMap


class _FakeProvider(ModelProvider):
    def __init__(self, tag: str) -> None:
        self.tag = tag

    def get_model(self, model_name: str | None) -> Model:
        # Return a sentinel tuple so tests can assert routing without constructing a real Model.
        return (self.tag, model_name)  # type: ignore[return-value]


def _map(tag: str = "myllm") -> tuple[MultiProviderMap, str]:
    pm = MultiProviderMap()
    pm.add_provider(tag, _FakeProvider(tag))
    return pm, tag


def test_default_provider_defaults_to_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTS_DEFAULT_PROVIDER", raising=False)
    mp = MultiProvider()
    # No custom default configured -> historical OpenAI default.
    assert mp._default_prefix is None


def test_bare_name_routes_to_default_provider() -> None:
    pm, tag = _map()
    mp = MultiProvider(provider_map=pm, default_provider=tag)
    assert mp.get_model("some-model") == (tag, "some-model")
    assert mp.get_model(None) == (tag, None)


def test_unknown_prefix_routes_to_default_provider_with_full_name() -> None:
    pm, tag = _map()
    mp = MultiProvider(provider_map=pm, default_provider=tag)
    # The whole "anthropic/claude-x" string is handed to the default provider verbatim.
    assert mp.get_model("anthropic/claude-x") == (tag, "anthropic/claude-x")


def test_explicit_prefix_still_wins_over_default() -> None:
    pm, tag = _map()
    other = MultiProviderMap()
    other.add_provider(tag, _FakeProvider(tag))
    other.add_provider("litellm-alias", _FakeProvider("aliased"))
    mp = MultiProvider(provider_map=other, default_provider=tag)
    assert mp.get_model("litellm-alias/x") == ("aliased", "x")


def test_env_var_configures_default_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    pm, tag = _map()
    monkeypatch.setenv("AGENTS_DEFAULT_PROVIDER", tag)
    mp = MultiProvider(provider_map=pm)
    assert mp.get_model("foo") == (tag, "foo")


def test_explicit_arg_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    pm = MultiProviderMap()
    pm.add_provider("a", _FakeProvider("a"))
    pm.add_provider("b", _FakeProvider("b"))
    monkeypatch.setenv("AGENTS_DEFAULT_PROVIDER", "a")
    mp = MultiProvider(provider_map=pm, default_provider="b")
    assert mp.get_model("foo") == ("b", "foo")


def test_openai_and_empty_normalize_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENTS_DEFAULT_PROVIDER", raising=False)
    assert MultiProvider(default_provider="openai")._default_prefix is None
    assert MultiProvider(default_provider="OpenAI")._default_prefix is None
    assert MultiProvider(default_provider="")._default_prefix is None


def test_unknown_default_provider_raises() -> None:
    with pytest.raises(UserError):
        MultiProvider(default_provider="does-not-exist")


def test_builtin_fallback_prefixes_are_valid_defaults() -> None:
    assert MultiProvider(default_provider="litellm")._default_prefix == "litellm"
    assert MultiProvider(default_provider="any-llm")._default_prefix == "any-llm"


def test_agents_default_model_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTS_DEFAULT_MODEL", "anthropic/claude-sonnet-4")
    assert get_default_model() == "anthropic/claude-sonnet-4"


def test_agents_default_model_takes_precedence_over_openai_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AGENTS_DEFAULT_MODEL", "gemini/gemini-2.0-flash")
    monkeypatch.setenv("OPENAI_DEFAULT_MODEL", "gpt-4.1")
    assert get_default_model() == "gemini/gemini-2.0-flash"


def test_agents_default_model_blank_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENTS_DEFAULT_MODEL", "   ")
    monkeypatch.setenv("OPENAI_DEFAULT_MODEL", "gpt-4.1")
    assert get_default_model() == "gpt-4.1"
