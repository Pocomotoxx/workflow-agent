"""Guarded, opt-in live run of a generated project.

Per the design, a generated system is presented statically first; a live run happens only after
explicit approval and is executed as a separate subprocess so a mistake in generated code cannot
run inline in your session.

Isolation caveat (be honest): a plain subprocess is NOT a security sandbox -- it shares your
network and filesystem. For real isolation, run generated projects inside the Agents SDK sandbox
extras / a container (see the repo's sandbox docs). This helper refuses to run unless the caller
passes ``confirm=True``, and never runs automatically.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ENTRY_BY_BACKEND = {
    "agents-python": "agent_system.py",
    "crewai": "crew.py",
}


class SandboxRefused(RuntimeError):
    """Raised when a live run is attempted without explicit confirmation."""


def run_generated(
    project_dir: str | Path,
    backend_name: str,
    *,
    confirm: bool = False,
    inputs: str = "",
    timeout: float = 300.0,
) -> subprocess.CompletedProcess[str]:
    """Run the generated project's entry point. Requires ``confirm=True``.

    Returns the completed process (stdout/stderr captured). The caller is responsible for having
    the required env vars/keys set in the environment; this function never injects secrets.
    """
    if not confirm:
        raise SandboxRefused(
            "Live run not confirmed. Review the static presentation first, then call with "
            "confirm=True. Prefer a container/sandbox for real isolation."
        )

    root = Path(project_dir)
    entry = ENTRY_BY_BACKEND.get(backend_name)
    if entry is None:
        raise ValueError(f"Unknown backend {backend_name!r}.")
    entry_path = root / entry
    if not entry_path.exists():
        raise FileNotFoundError(f"Entry point not found: {entry_path}")

    return subprocess.run(
        [sys.executable, entry, inputs] if inputs else [sys.executable, entry],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
