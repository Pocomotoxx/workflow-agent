"""The architect agent: turns a natural-language task into a structured ``SystemSpec``."""

from __future__ import annotations

from agents import Agent
from agents.models.interface import Model

from .spec import SystemSpec

_INSTRUCTIONS = (
    "You are a multi-agent systems architect. Given a task (and optionally available MCP servers "
    "and access notes), design a small, coherent multi-agent system as a SystemSpec.\n"
    "Rules:\n"
    "- Prefer 2-5 agents with clear, non-overlapping roles.\n"
    "- Define tasks that reference real agents, ordered via depends_on (ids of earlier tasks).\n"
    "- Put only env var NAMES in required_env (e.g. OPENAI_API_KEY, TAVILY_API_KEY). Never invent "
    "or include secret values.\n"
    "- If MCP servers are provided, wire relevant ones into agents.tools as 'mcp:<server_name>'.\n"
    "- Keep the design provider-agnostic; do not hardcode a specific model."
)


def build_architect(model: str | Model | None = None) -> Agent:
    return Agent(
        name="system-architect",
        model=model,
        instructions=_INSTRUCTIONS,
        output_type=SystemSpec,
    )
