# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

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
    key: str | None = typer.Option(None, "--key", help="Idempotency key."),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    cfg = load_config()
    state = DetourState(cfg.state_file)
    try:
        result = state.start(title, force=force, key=key)
    except StateError as exc:
        _fail(exc)
    if result.created:
        append_event(
            cfg.notes_dir,
            cfg.section_heading,
            datetime.now(),
            cfg.time_format,
            0,
            "started",
            title,
        )
    _print_result("start", state.load(), result.created, json_output, f"Started: {title}")


@app.command("into")
def into_detour(
    title: str,
    key: str | None = typer.Option(None, "--key", help="Idempotency key."),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    cfg = load_config()
    state = DetourState(cfg.state_file)
    try:
        result = state.push(title, key=key)
    except StateError as exc:
        _fail(exc)
    if result.created:
        append_event(
            cfg.notes_dir,
            cfg.section_heading,
            datetime.now(),
            cfg.time_format,
            result.depth,
            "detour",
            title,
        )
    _print_result("into", state.load(), result.created, json_output, f"Detour: {title}")


@app.command()
def done(
    note: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _pop_with_event("done", note, json_output)


@app.command()
def back(
    note: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _pop_with_event("back", note, json_output)


@app.command()
def log(
    message: str,
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
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
    _print_result("log", stack, True, json_output, "Logged.")


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    cfg = load_config()
    stack = DetourState(cfg.state_file).load()
    if json_output:
        _print_json(_stack_payload("status", stack, created=False))
        return
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


@app.command()
def event(
    payload: str,
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        _fail(StateError(f"Invalid event JSON: {exc.msg}"))
    if not isinstance(data, dict):
        _fail(StateError("Event JSON must be an object."))

    event_type = data.get("type")
    title = data.get("title")
    note = data.get("note")
    key = data.get("key")
    if key is not None and not isinstance(key, str):
        _fail(StateError("Event key must be a string."))

    if event_type == "start":
        if not isinstance(title, str):
            _fail(StateError("Event title must be a string."))
        start(title, force=False, key=key, json_output=json_output)
    elif event_type == "into":
        if not isinstance(title, str):
            _fail(StateError("Event title must be a string."))
        into_detour(title, key=key, json_output=json_output)
    elif event_type == "done":
        if note is not None and not isinstance(note, str):
            _fail(StateError("Event note must be a string."))
        done(note, json_output=json_output)
    elif event_type == "back":
        if note is not None and not isinstance(note, str):
            _fail(StateError("Event note must be a string."))
        back(note, json_output=json_output)
    elif event_type == "log":
        message = data.get("message")
        if not isinstance(message, str):
            _fail(StateError("Event message must be a string."))
        log(message, json_output=json_output)
    else:
        _fail(StateError("Event type must be one of start, into, done, back, or log."))


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


def _pop_with_event(action: str, note: str | None, json_output: bool) -> None:
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
    _print_result(
        action,
        state.load(),
        True,
        json_output,
        f"{action.title()}: {item.title}{suffix}",
    )


def _fail(exc: StateError) -> None:
    console.print(f"[red]{exc}[/red]")
    raise typer.Exit(1)


def _print_result(
    action: str,
    stack: list[Any],
    created: bool,
    json_output: bool,
    human_message: str,
) -> None:
    if json_output:
        _print_json(_stack_payload(action, stack, created))
        return
    console.print(human_message)


def _stack_payload(action: str, stack: list[Any], created: bool) -> dict[str, Any]:
    return {
        "status": "ok",
        "action": action,
        "created": created,
        "stack_depth": len(stack),
        "current": stack[-1].title if stack else None,
        "stack": [item.to_dict() for item in stack],
    }


def _print_json(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    app()
