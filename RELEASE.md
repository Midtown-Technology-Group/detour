# Release Process

`detour` is a small CLI, so releases should stay boring and repeatable.

## Preflight

Run from the repository root:

```powershell
python -m pytest --cov=detour --cov-report=term-missing
python -m ruff check .
python -m mypy src/detour
python -m build
python -m twine check dist/*
python -m pip_audit .
```

## Tag

Update `pyproject.toml` and `CHANGELOG.md`, commit the change, then tag:

```powershell
git tag -a vX.Y.Z -m "detour vX.Y.Z"
git push origin main --tags
```

## Install Check

After the tag is pushed:

```powershell
pipx install git+https://github.com/Midtown-Technology-Group/detour.git@vX.Y.Z
detour --help
```
