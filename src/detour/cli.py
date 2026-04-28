# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from datetime import datetime

import typer
from rich.console import Console
from rich.tree import Tree

from .config import load_config
from .notes import append_event
from .state import DetourState, StateError

app = typer.Typer(help="Track work detours in a small stack and daily Markdown notes.")
console = Console()


@app.command()
def start(
    title: str,
    force: bool = typer.Option(False, "--force", help="Replace an active stack."),
) -> None:
    cfg = load_config()
    state = DetourState(cfg.state_file)
    try:
        state.start(title, force=force)
    except StateError as exc:
        _fail(exc)
    append_event(
        cfg.notes_dir,
        cfg.section_heading,
        datetime.now(),
        cfg.time_format,
        0,
        "started",
        title,
    )
    console.print(f"Started: {title}")


@app.command("into")
def into_detour(title: str) -> None:
    cfg = load_config()
    state = DetourState(cfg.state_file)
    try:
        depth = state.push(title)
    except StateError as exc:
        _fail(exc)
    append_event(
        cfg.notes_dir,
        cfg.section_heading,
        datetime.now(),
        cfg.time_format,
        depth,
        "detour",
        title,
    )
    console.print(f"Detour: {title}")


@app.command()
def done(note: str | None = typer.Argument(None)) -> None:
    _pop_with_event("done", note)


@app.command()
def back(note: str | None = typer.Argument(None)) -> None:
    _pop_with_event("back", note)


@app.command()
def log(message: str) -> None:
    cfg = load_config()
    state = DetourState(cfg.state_file)
    stack = state.load()
    if not stack:
        _fail(StateError("No active detour."))
    append_event(
        cfg.notes_dir,
        cfg.section_heading,
        datetime.now(),
        cfg.time_format,
        len(stack) - 1,
        "note",
        message,
    )
    console.print("Logged.")


@app.command()
def status() -> None:
    cfg = load_config()
    stack = DetourState(cfg.state_file).load()
    if not stack:
        console.print("No active detour.")
        return

    root = Tree(stack[0].title)
    node = root
    for item in stack[1:]:
        node = node.add(item.title)
    console.print(root)


@app.command()
def reset(yes: bool = typer.Option(False, "--yes", help="Clear the active stack.")) -> None:
    if not yes:
        _fail(StateError("Pass --yes to reset the active stack."))
    cfg = load_config()
    DetourState(cfg.state_file).reset()
    console.print("Reset.")


@app.command("config")
def show_config() -> None:
    cfg = load_config()
    console.print(f"config_dir: {cfg.config_dir}")
    console.print(f"config_file: {cfg.config_file}")
    console.print(f"state_dir: {cfg.state_dir}")
    console.print(f"state_file: {cfg.state_file}")
    console.print(f"notes_dir: {cfg.notes_dir}")
    console.print(f"section_heading: {cfg.section_heading}")
    console.print(f"time_format: {cfg.time_format}")


def _pop_with_event(action: str, note: str | None) -> None:
    cfg = load_config()
    state = DetourState(cfg.state_file)
    stack = state.load()
    if not stack:
        _fail(StateError("No active detour."))
    depth = len(stack) - 1
    try:
        item = state.pop()
    except StateError as exc:
        _fail(exc)
    append_event(
        cfg.notes_dir,
        cfg.section_heading,
        datetime.now(),
        cfg.time_format,
        depth,
        action,
        note,
    )
    suffix = f": {note}" if note else ""
    console.print(f"{action.title()}: {item.title}{suffix}")


def _fail(exc: StateError) -> None:
    console.print(f"[red]{exc}[/red]")
    raise typer.Exit(1)


if __name__ == "__main__":
    app()
