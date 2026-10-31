# Repository guidance

`detour` is a Python CLI that maintains per-agent active stacks in JSON and appends timestamped events to daily Markdown or LogSeq notes. `src/detour/` contains the package, `tests/` its tests, and `site/` the Astro project site. Read `README.md`, `CONTRIBUTING.md`, and `SECURITY.md` before implementation.

## Verification

Use Python 3.11+; CI covers Python 3.11/3.12 on Linux and Windows. From the root, install the development extras and run:

```sh
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy src/detour
python -m pytest --cov=detour --cov-report=term-missing
```

Branch coverage is configured with a 75% floor. Package changes also need `python -m build`, `python -m twine check dist/*`, and `python -m pip_audit .` as in CI. Site changes use root npm scripts (`npm ci`, `npm run build`) with Node 24 in CI.

## Persistent state

Tests and development smoke commands must use disposable `DETOUR_CONFIG_DIR`, `DETOUR_STATE_DIR`, and `DETOUR_NOTES_DIR` locations. Do not reset or rewrite an operator's real stack or journal. Preserve legacy single-stack loading as the default agent, independent per-agent stacks, `--key` idempotency, and Markdown/LogSeq output conventions. `merge` appends a snapshot without changing stack state; preserve that distinction.

Releases require matching package version and `vX.Y.Z` tag; `.github/workflows/release.yml` verifies and publishes distributions. Version/tag pushes are release actions, not verification shortcuts. Windows MSI installation/uninstallation is per-machine and elevated; use a disposable target for installer testing. Preserve AGPL-3.0-only notices.
