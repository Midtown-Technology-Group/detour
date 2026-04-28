from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path


def append_event(
    notes_dir: Path,
    section_heading: str,
    when: datetime,
    time_format: str,
    depth: int,
    action: str,
    message: str | None = None,
) -> Path:
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_path = notes_dir / f"{when:%Y-%m-%d}.md"
    text = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
    text = _ensure_section(text, section_heading)
    line = _format_event(when, time_format, depth, action, message)
    text = text + line if text.endswith("\n\n") else text.rstrip() + "\n" + line
    _atomic_write(note_path, text)
    return note_path


def _ensure_section(text: str, section_heading: str) -> str:
    if not text:
        return f"{section_heading}\n\n"
    if section_heading in text.splitlines():
        return text
    return text.rstrip() + f"\n\n{section_heading}\n\n"


def _format_event(
    when: datetime,
    time_format: str,
    depth: int,
    action: str,
    message: str | None,
) -> str:
    indent = "  " * depth
    suffix = f": {message}" if message else ""
    return f"{indent}- {when.strftime(time_format)} {action}{suffix}\n"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
