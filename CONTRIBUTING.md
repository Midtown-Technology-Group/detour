# Contributing

Thanks for helping improve `detour`.

## Development Setup

Use Python 3.11 or newer.

```powershell
python -m pip install -e ".[dev]"
python -m pytest --cov=detour --cov-report=term-missing
python -m ruff check .
python -m mypy src/detour
```

The package exposes the `detour` console script through `pyproject.toml`.

## Pull Requests

- Keep changes small and reviewable.
- Add or update tests for behavior changes.
- Keep CLI output concise and human-readable.
- Preserve JSON output compatibility for agent-facing commands.
- Do not write to user notes in tests without `DETOUR_*` environment overrides.

## Release Changes

For release-bound changes, update:

- `pyproject.toml`
- `CHANGELOG.md`
- docs that mention commands or config

Releases are tag-driven. See [RELEASE.md](RELEASE.md).
