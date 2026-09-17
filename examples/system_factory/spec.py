"""Structured system specification produced by the architect and consumed by generators.

The architect agent emits a ``SystemSpec`` (structured output). Backends turn that spec into a
runnable project. Keeping the spec framework-neutral is what makes the generator pluggable across
CrewAI, the Agents SDK, and (potentially) other backends.

Secrets are never stored here: only the *names* of required environment variables (e.g.
``OPENAI_API_KEY``). The user supplies the actual values in their own environment; the generator
emits an ``.env.example`` listing the names, never the values.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentSpec(BaseModel):
    """One agent/role in the generated system."""

    name: str = Field(description="Unique snake_case identifier, e.g. 'researcher'.")
    role: str = Field(description="Short role title, e.g. 'Senior Research Analyst'.")
    goal: str = Field(description="What this agent is trying to achieve.")
    backstory: str = Field(
        default="",
        description="Optional persona/context that shapes the agent's behavior.",
    )
    tools: list[str] = Field(
        default_factory=list,
        description="Names of tools this agent uses (must match a name in SystemSpec.mcp_servers "
        "or be a well-known built-in). Free-form; backends map what they can.",
    )


class TaskSpec(BaseModel):
    """One unit of work assigned to an agent, with optional ordering dependencies."""

    id: str = Field(description="Short unique id, e.g. 't1'.")
    description: str = Field(description="What to do. Self-contained.")
    agent: str = Field(description="AgentSpec.name responsible for this task.")
    expected_output: str = Field(
        default="",
        description="What a good result looks like (used by CrewAI's expected_output).",
    )
    depends_on: list[str] = Field(
        default_factory=list,
        description="Ids of tasks that must complete first. Empty if independent.",
    )


class MCPServerSpec(BaseModel):
    """An MCP server the generated system should connect to."""

    name: str = Field(description="Identifier used to reference this server from agents.tools.")
    command: str = Field(
        default="",
        description="Executable for a stdio MCP server (e.g. 'npx'). Empty if url-based.",
    )
    args: list[str] = Field(default_factory=list, description="Args for the stdio command.")
    url: str = Field(default="", description="URL for an HTTP/SSE MCP server. Empty if stdio.")


class SystemSpec(BaseModel):
    """A framework-neutral description of a multi-agent system to generate."""

    name: str = Field(description="Project name in snake_case, e.g. 'market_research_crew'.")
    description: str = Field(description="One-paragraph summary of what the system does.")
    provider_env: str = Field(
        default="AGENTS_DEFAULT_PROVIDER",
        description="Env var selecting the model provider (provider-agnostic default).",
    )
    model_env: str = Field(
        default="AGENTS_DEFAULT_MODEL",
        description="Env var selecting the model id.",
    )
    required_env: list[str] = Field(
        default_factory=list,
        description="Names of env vars the system needs (API keys, etc.). Names only, no values.",
    )
    agents: list[AgentSpec]
    tasks: list[TaskSpec]
    mcp_servers: list[MCPServerSpec] = Field(default_factory=list)

    def agent_names(self) -> set[str]:
        return {a.name for a in self.agents}
