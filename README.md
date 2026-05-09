# detour

[![CI](https://github.com/Midtown-Technology-Group/detour/actions/workflows/ci.yml/badge.svg)](https://github.com/Midtown-Technology-Group/detour/actions/workflows/ci.yml)
[![Release](https://github.com/Midtown-Technology-Group/detour/actions/workflows/release.yml/badge.svg)](https://github.com/Midtown-Technology-Group/detour/actions/workflows/release.yml)
[![GitHub release](https://img.shields.io/github/v/release/Midtown-Technology-Group/detour)](https://github.com/Midtown-Technology-Group/detour/releases)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License: AGPL-3.0-only](https://img.shields.io/badge/license-AGPL--3.0--only-orange)](LICENSE)
[![Coverage gate](https://img.shields.io/badge/coverage%20gate-%E2%89%A575%25-brightgreen)](pyproject.toml)
[![OpenSSF checklist](https://img.shields.io/badge/OpenSSF-best%20practices%20checklist-informational)](https://www.bestpractices.dev/en/criteria/0)

`detour` tracks the work you did to get back to the work you meant to do.

It keeps a small active stack in JSON and appends timestamped events to daily
Markdown notes.

## Install

```powershell
pipx install -e .
```

Tagged releases can be installed directly from GitHub:

```powershell
pipx install git+https://github.com/Midtown-Technology-Group/detour.git@v0.1.3
```

Optional shell alias:

```powershell
Set-Alias dt detour
```

## Usage

```powershell
detour start "Fix deploy"
detour into "Refresh kubeconfig"
detour into "Debug SSO role"
detour done "Role expired"
detour done
detour done "Deploy fixed"
```

Other useful commands:

```powershell
detour status
detour status --json
detour agents
detour merge
detour log "Found the expired role assignment"
detour pothole "SSO token expired mid-deploy"
detour back "Not needed after all"
detour reset --yes
detour config
```

Agent-friendly structured output is available with `--json`:

```powershell
detour into "Refresh kubeconfig" --key kubeconfig-refresh --json
detour event '{"type":"into","title":"Debug SSO role","key":"debug-sso-role"}' --json
```

`--key` is an idempotency guard. If the current stack item already has the same
key, `detour` returns success without pushing a duplicate item.

## Multi-Agent State

By default, commands use the `default` agent stack. Agents can avoid stepping on
each other by setting `DETOUR_AGENT` or passing `--agent` before the command:

```powershell
$env:DETOUR_AGENT = "codex-detour-site"
detour start "Fix project site"

detour --agent "codex-ci-debug" start "Investigate failing CI"
detour agents
detour merge
```

All agent stacks share the same state file, but each agent has an independent
active chain. Existing single-stack state files load as the `default` agent.

Use `detour merge` to append a road-themed snapshot of all active agent lanes to
today's daily note without changing any stack state.

## Files

By default, `detour` uses:

- Config: `~/.config/detour/config.toml`
- State: `~/.local/state/detour/stack.json`
- Notes: `~/notes/daily/YYYY-MM-DD.md`

Config example:

```toml
notes_dir = "~/notes/daily"
section_heading = "## Detours"
time_format = "%H:%M"
note_filename_format = "%Y-%m-%d"
note_style = "markdown"
```

LogSeq-backed journals can use the existing journal directory and underscore
filenames:

```toml
notes_dir = "~/OneDrive - Midtown Technology Group LLC/Knowledge/daily"
section_heading = "Detours"
time_format = "%H:%M"
note_filename_format = "%Y_%m_%d"
note_style = "logseq"
```

For tests or local overrides, these environment variables are supported:

- `DETOUR_CONFIG_DIR`
- `DETOUR_STATE_DIR`
- `DETOUR_NOTES_DIR`
- `DETOUR_AGENT`

## Markdown

```md
## Detours

- 09:12 started: Fix deploy
  - 09:16 detour: Refresh kubeconfig
    - 09:18 detour: Debug SSO role
    - 09:24 done: Role expired
  - 09:25 done
- 09:42 done: Deploy fixed
```

## License

Copyright (C) 2026 Midtown Technology Group LLC.

AGPL-3.0-only. See [LICENSE](LICENSE).

## Project Site

The Astro project site lives in `site/`.

```powershell
npm install
npm run dev
npm run build
```

## Releases

Releases are tag-driven. Update `project.version` in `pyproject.toml`, commit the
change, then push a matching `vX.Y.Z` tag:

```powershell
git tag vX.Y.Z
git push origin vX.Y.Z
```

The release workflow verifies the tag matches the package version, runs checks,
builds the source distribution and wheel, and publishes a GitHub Release with the
distribution files attached.

## Project Maturity

`detour` uses pytest with branch-aware coverage, ruff, mypy, package build
checks, and dependency audits in CI. For broader FOSS hygiene, use the OpenSSF
Best Practices Badge criteria as the project checklist.

Project process docs:

- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Support](SUPPORT.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## Windows MSI

Tagged releases build a per-machine Windows MSI that installs `detour.exe` under `Program Files` and adds that install directory to the system PATH. Installing or uninstalling the MSI requires an elevated prompt.
