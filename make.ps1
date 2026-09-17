#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Cross-platform task runner mirroring the common Makefile targets, for developers on Windows
    (or anywhere `make`/`bash` is not available). PowerShell 7+ (pwsh) runs on Windows, macOS and
    Linux.

.DESCRIPTION
    This is a convenience wrapper around the same `uv run ...` commands the Makefile uses for the
    day-to-day development loop. The Makefile remains the source of truth and is used by CI; this
    script intentionally covers only the targets a contributor runs locally. Targets that shell out
    to bash-only helpers or Unix-only integration runners are deliberately omitted.

.EXAMPLE
    ./make.ps1 sync
    ./make.ps1 check
    ./make.ps1 tests
    ./make.ps1 format
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Target = 'help',

    # Extra args forwarded to the underlying tool (e.g. ./make.ps1 tests -- -k my_test).
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = 'Stop'
# Run from the repo root (this script's directory) regardless of the caller's cwd.
Set-Location -LiteralPath $PSScriptRoot

function Invoke-Step {
    param([Parameter(Mandatory)][string[]]$Command)
    Write-Host ">> $($Command -join ' ')" -ForegroundColor Cyan
    & $Command[0] @($Command[1..($Command.Length - 1)])
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $($Command -join ' ')"
    }
}

$normalized = $Target.ToLowerInvariant()
$helpTargets = @('help', '-h', '--help', '/?')
if ($normalized -notin $helpTargets -and -not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv was not found on PATH. Install it from https://docs.astral.sh/uv/ first."
}

switch ($normalized) {
    'sync' {
        Invoke-Step @('uv', 'sync', '--all-extras', '--all-packages', '--group', 'dev')
    }
    'format' {
        Invoke-Step @('uv', 'run', 'ruff', 'format')
        Invoke-Step @('uv', 'run', 'ruff', 'check', '--fix')
    }
    'format-check' {
        Invoke-Step @('uv', 'run', 'ruff', 'format', '--check')
    }
    'lint' {
        Invoke-Step @('uv', 'run', 'ruff', 'check')
        Invoke-Step @('uv', 'run', 'python', '.github/scripts/check_optional_truthiness.py', 'src/agents')
    }
    'mypy' {
        Invoke-Step @('uv', 'run', 'mypy', 'src')
    }
    'pyright' {
        $threads = if ($env:PYRIGHT_THREADS) { $env:PYRIGHT_THREADS } else { '4' }
        Invoke-Step @('uv', 'run', 'pyright', '--project', 'pyrightconfig.json', '--threads', $threads)
    }
    'typecheck' {
        # PowerShell has no `make -j`; run the two type checkers sequentially.
        Invoke-Step @('uv', 'run', 'mypy', 'src')
        $threads = if ($env:PYRIGHT_THREADS) { $env:PYRIGHT_THREADS } else { '4' }
        Invoke-Step @('uv', 'run', 'pyright', '--project', 'pyrightconfig.json', '--threads', $threads)
    }
    'tests' {
        Invoke-Step (@('uv', 'run', 'pytest', '-m', 'not serial') + $Rest)
        Invoke-Step @('uv', 'run', 'python', '.github/scripts/run_serial_tests.py')
    }
    'tests-parallel' {
        $workers = if ($env:PYTEST_XDIST_AUTO_NUM_WORKERS) { $env:PYTEST_XDIST_AUTO_NUM_WORKERS } else { 'auto' }
        Invoke-Step (@('uv', 'run', 'pytest', '-n', $workers, '--dist', 'worksteal', '-m', 'not serial') + $Rest)
    }
    'tests-serial' {
        Invoke-Step @('uv', 'run', 'python', '.github/scripts/run_serial_tests.py')
    }
    'coverage' {
        Invoke-Step @('uv', 'run', 'coverage', 'run', '-m', 'pytest')
        Invoke-Step @('uv', 'run', 'coverage', 'xml', '-o', 'coverage.xml')
        Invoke-Step @('uv', 'run', 'coverage', 'report', '-m', '--fail-under=85')
    }
    'snapshots-fix' {
        Invoke-Step @('uv', 'run', 'pytest', '--inline-snapshot=fix')
    }
    'snapshots-create' {
        Invoke-Step @('uv', 'run', 'pytest', '--inline-snapshot=create')
    }
    'build-docs' {
        Invoke-Step @('uv', 'run', 'docs/scripts/generate_ref_files.py')
        Invoke-Step @('uv', 'run', 'mkdocs', 'build')
    }
    'serve-docs' {
        Invoke-Step @('uv', 'run', 'mkdocs', 'serve')
    }
    'check' {
        Invoke-Step @('uv', 'run', 'ruff', 'format', '--check')
        Invoke-Step @('uv', 'run', 'ruff', 'check')
        Invoke-Step @('uv', 'run', 'python', '.github/scripts/check_optional_truthiness.py', 'src/agents')
        Invoke-Step @('uv', 'run', 'mypy', 'src')
        $threads = if ($env:PYRIGHT_THREADS) { $env:PYRIGHT_THREADS } else { '4' }
        Invoke-Step @('uv', 'run', 'pyright', '--project', 'pyrightconfig.json', '--threads', $threads)
        Invoke-Step @('uv', 'run', 'pytest', '-m', 'not serial')
        Invoke-Step @('uv', 'run', 'python', '.github/scripts/run_serial_tests.py')
    }
    default {
        @"
Usage: ./make.ps1 <target> [-- extra args]

Cross-platform wrapper for the common Makefile targets (needs 'uv' on PATH).

  sync              Install all extras/packages and the dev group
  format            ruff format + ruff check --fix
  format-check      ruff format --check
  lint              ruff check + optional-truthiness check
  mypy              mypy src
  pyright           pyright (honors PYRIGHT_THREADS)
  typecheck         mypy + pyright (sequential)
  tests             parallel non-serial tests, then serial tests
  tests-parallel    non-serial tests only (honors PYTEST_XDIST_AUTO_NUM_WORKERS)
  tests-serial      serial tests only
  coverage          coverage run + xml + report (--fail-under=85)
  snapshots-fix     pytest --inline-snapshot=fix
  snapshots-create  pytest --inline-snapshot=create
  build-docs        generate ref files + mkdocs build
  serve-docs        mkdocs serve
  check             format-check + lint + typecheck + tests

For integration tests and other CI-only targets, use the Makefile on a Unix shell.
"@ | Write-Host
        if ($Target -notin @('help', '-h', '--help', '/?')) {
            Write-Host "`nUnknown target: '$Target'" -ForegroundColor Yellow
            exit 2
        }
    }
}
