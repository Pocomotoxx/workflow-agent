"""Build a static presentation of a generated system: overview, architecture diagram, dry-run."""

from __future__ import annotations

from .spec import SystemSpec


def mermaid_diagram(spec: SystemSpec) -> str:
    """A Mermaid flowchart of the task graph, annotated with the responsible agent."""
    lines = ["flowchart TD"]
    for task in spec.tasks:
        label = f"{task.id}: {task.agent}"
        lines.append(f"    {task.id}[{label}]")
    for task in spec.tasks:
        for dep in task.depends_on:
            lines.append(f"    {dep} --> {task.id}")
    return "\n".join(lines)


def presentation(spec: SystemSpec, backend_name: str, files: dict[str, str]) -> str:
    """A Markdown presentation: what was built, the architecture, and how to run it."""
    agents_md = "\n".join(f"- **{a.name}** ({a.role}) — {a.goal}" for a in spec.agents)
    tasks_md = "\n".join(
        f"- `{t.id}` → **{t.agent}**"
        + (f" (after {', '.join(t.depends_on)})" if t.depends_on else " (independent)")
        for t in spec.tasks
    )
    mcp_md = "\n".join(f"- {s.name}" for s in spec.mcp_servers) if spec.mcp_servers else "- (none)"
    files_md = "\n".join(
        f"- `{path}` ({len(content.splitlines())} lines)" for path, content in sorted(files.items())
    )
    return f"""# {spec.name}

{spec.description}

**Backend:** `{backend_name}` · **Agents:** {len(spec.agents)} · **Tasks:** {len(spec.tasks)}

## Architecture

```mermaid
{mermaid_diagram(spec)}
```

## Agents

{agents_md}

## Task flow

{tasks_md}

## MCP servers

{mcp_md}

## Generated files

{files_md}

## Required environment (names only — you provide the values)

{chr(10).join(f"- `{name}`" for name in spec.required_env) or "- (none)"}

## How to run

See the generated `README.md`. The system is provider-agnostic: set `{spec.provider_env}` and
`{spec.model_env}` to target any provider. A live run is offered only after you approve it, and is
executed in a sandbox so nothing leaves your machine by mistake.
"""
