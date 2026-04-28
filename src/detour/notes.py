# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

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
    note_filename_format: str = "%Y-%m-%d",
    note_style: str = "markdown",
) -> Path:
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_path = notes_dir / f"{when.strftime(note_filename_format)}.md"
    text = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
    if note_style == "logseq":
        text = _append_logseq_event(
            text,
            section_heading,
            when,
            time_format,
            depth,
            action,
            message,
        )
        _atomic_write(note_path, text)
        return note_path
    if note_style != "markdown":
        raise ValueError("note_style must be markdown or logseq")
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


def _append_logseq_event(
    text: str,
    section_heading: str,
    when: datetime,
    time_format: str,
    depth: int,
    action: str,
    message: str | None,
) -> str:
    heading = section_heading.removeprefix("-").strip()
    section_line = f"- {heading}"
    line = _format_logseq_event(when, time_format, depth, action, message)
    if not text:
        return f"{section_line}\n{line}"

    lines = text.splitlines(keepends=True)
    section_index = _find_logseq_section(lines, section_line)
    if section_index is None:
        prefix = "" if text.endswith("\n") else "\n"
        return f"{text}{prefix}{section_line}\n{line}"

    insert_at = section_index + 1
    while insert_at < len(lines):
        candidate = lines[insert_at]
        if candidate.strip() and not candidate.startswith(("\t", " ")):
            break
        insert_at += 1
    lines.insert(insert_at, line)
    return "".join(lines)


def _find_logseq_section(lines: list[str], section_line: str) -> int | None:
    for index, line in enumerate(lines):
        if line.strip() == section_line:
            return index
    return None


def _format_logseq_event(
    when: datetime,
    time_format: str,
    depth: int,
    action: str,
    message: str | None,
) -> str:
    indent = "\t" * (depth + 1)
    suffix = f": {message}" if message else ""
    return f"{indent}- {when.strftime(time_format)} {action}{suffix}\n"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
