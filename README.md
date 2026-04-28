# detour

![CI](https://github.com/Midtown-Technology-Group/detour/actions/workflows/ci.yml/badge.svg)

`detour` tracks the work you did to get back to the work you meant to do.

It keeps a small active stack in JSON and appends timestamped events to daily
Markdown notes.

## Install

```powershell
pipx install -e .
```

Tagged releases can be installed directly from GitHub:

```powershell
pipx install git+https://github.com/Midtown-Technology-Group/detour.git@v0.1.0
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
detour log "Found the expired role assignment"
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
```

For tests or local overrides, these environment variables are supported:

- `DETOUR_CONFIG_DIR`
- `DETOUR_STATE_DIR`
- `DETOUR_NOTES_DIR`

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
