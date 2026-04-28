from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir, user_state_dir


@dataclass(frozen=True)
class DetourConfig:
    config_dir: Path
    config_file: Path
    state_dir: Path
    state_file: Path
    notes_dir: Path
    section_heading: str
    time_format: str


def load_config() -> DetourConfig:
    config_dir = _path_from_env("DETOUR_CONFIG_DIR") or Path(user_config_dir("detour"))
    state_dir = _path_from_env("DETOUR_STATE_DIR") or Path(user_state_dir("detour"))
    config_file = config_dir / "config.toml"

    data: dict[str, str] = {}
    if config_file.exists():
        data = tomllib.loads(config_file.read_text(encoding="utf-8"))

    notes_dir = (
        _path_from_env("DETOUR_NOTES_DIR")
        or _expand_path(data.get("notes_dir", "~/notes/daily"))
    )
    section_heading = data.get("section_heading", "## Detours")
    time_format = data.get("time_format", "%H:%M")

    return DetourConfig(
        config_dir=config_dir,
        config_file=config_file,
        state_dir=state_dir,
        state_file=state_dir / "stack.json",
        notes_dir=notes_dir,
        section_heading=section_heading,
        time_format=time_format,
    )


def _path_from_env(name: str) -> Path | None:
    value = os.environ.get(name)
    if not value:
        return None
    return _expand_path(value)


def _expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()
