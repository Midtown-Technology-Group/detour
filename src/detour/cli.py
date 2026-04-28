# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import typer
from rich.console import Console
from rich.tree import Tree

from .config import DetourConfig, load_config
from .notes import append_event
from .state import DetourState, StateError

app = typer.Typer(help="Track work detours in a small stack and daily Markdown notes.")
console = Console()


@app.callback()
def main(
    ctx: typer.Context,
    agent: str | None = typer.Option(
        None,
        "--agent",
        help="Use a named agent stack. Defaults to DETOUR_AGENT or config.",
    ),
) -> None:
    ctx.obj = {"agent": agent} if agent else {}


@app.command()
def start(
    ctx: typer.Context,
    title: str,
    force: bool = typer.Option(False, "--force", help="Replace an active stack."),
    key: str | None = typer.Option(None, "--key", help="Idempotency key."),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _start(ctx, title, force, key, json_output)


def _start(
    ctx: typer.Context,
    title: str,
    force: bool,
    key: str | None,
    json_output: bool,
) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
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
    _print_result(
        state.agent,
        "start",
        state.load(),
        result.created,
        json_output,
        f"Started: {title}",
    )


@app.command("into")
def into_detour(
    ctx: typer.Context,
    title: str,
    key: str | None = typer.Option(None, "--key", help="Idempotency key."),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _into(ctx, title, key, json_output)


def _into(ctx: typer.Context, title: str, key: str | None, json_output: bool) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
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
    _print_result(
        state.agent,
        "into",
        state.load(),
        result.created,
        json_output,
        f"Detour: {title}",
    )


@app.command()
def done(
    ctx: typer.Context,
    note: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _pop_with_event(ctx, "done", note, json_output)


@app.command()
def back(
    ctx: typer.Context,
    note: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _pop_with_event(ctx, "back", note, json_output)


@app.command()
def log(
    ctx: typer.Context,
    message: str,
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    _log(ctx, message, json_output)


@app.command()
def status(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
    stack = state.load()
    if json_output:
        _print_json(_stack_payload(state.agent, "status", stack, created=False))
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
def reset(
    ctx: typer.Context,
    yes: bool = typer.Option(False, "--yes", help="Clear the active stack."),
) -> None:
    if not yes:
        _fail(StateError("Pass --yes to reset the active stack."))
    cfg = load_config()
    _state(cfg, ctx).reset()
    console.print("Reset.")


@app.command()
def event(
    ctx: typer.Context,
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
        _start(ctx, title, force=False, key=key, json_output=json_output)
    elif event_type == "into":
        if not isinstance(title, str):
            _fail(StateError("Event title must be a string."))
        _into(ctx, title, key=key, json_output=json_output)
    elif event_type == "done":
        if note is not None and not isinstance(note, str):
            _fail(StateError("Event note must be a string."))
        _pop_with_event(ctx, "done", note, json_output)
    elif event_type == "back":
        if note is not None and not isinstance(note, str):
            _fail(StateError("Event note must be a string."))
        _pop_with_event(ctx, "back", note, json_output)
    elif event_type == "log":
        message = data.get("message")
        if not isinstance(message, str):
            _fail(StateError("Event message must be a string."))
        _log(ctx, message, json_output)
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
    console.print(f"agent_name: {cfg.agent_name}")


@app.command()
def agents(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
    payload = {
        agent: {
            "stack_depth": len(stack),
            "current": stack[-1].title if stack else None,
        }
        for agent, stack in state.load_all().items()
    }
    if json_output:
        _print_json({"status": "ok", "action": "agents", "agent": state.agent, "agents": payload})
        return
    if not payload:
        console.print("No active agent stacks.")
        return
    for agent, summary in payload.items():
        console.print(f"{agent}: {summary['current']} ({summary['stack_depth']})")


@app.command()
def merge(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Print structured JSON output."),
) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
    lanes = {
        agent: [item.title for item in stack]
        for agent, stack in state.load_all().items()
        if stack
    }
    if not lanes:
        _fail(StateError("No active agent lanes to merge."))

    now = datetime.now()
    note_path = append_event(
        cfg.notes_dir,
        cfg.section_heading,
        now,
        cfg.time_format,
        0,
        "merge",
        "active lanes",
    )
    for agent, titles in lanes.items():
        note_path = append_event(
            cfg.notes_dir,
            cfg.section_heading,
            now,
            cfg.time_format,
            1,
            f"lane {agent}",
            " -> ".join(titles),
        )

    if json_output:
        _print_json(
            {
                "status": "ok",
                "action": "merge",
                "agent": state.agent,
                "note": str(note_path),
                "lanes": lanes,
            }
        )
        return
    console.print(f"Merged {len(lanes)} lane(s) into {note_path}.")


def _pop_with_event(ctx: typer.Context, action: str, note: str | None, json_output: bool) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
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
        state.agent,
        action,
        state.load(),
        True,
        json_output,
        f"{action.title()}: {item.title}{suffix}",
    )


def _log(ctx: typer.Context, message: str, json_output: bool) -> None:
    cfg = load_config()
    state = _state(cfg, ctx)
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
    _print_result(state.agent, "log", stack, True, json_output, "Logged.")


def _state(cfg: DetourConfig, ctx: typer.Context) -> DetourState:
    return DetourState(cfg.state_file, agent=_agent_name(cfg, ctx))


def _agent_name(cfg: DetourConfig, ctx: typer.Context) -> str:
    obj = ctx.obj if isinstance(ctx.obj, dict) else {}
    value = obj.get("agent") or cfg.agent_name
    if not isinstance(value, str):
        raise StateError("Agent name must be a string.")
    return value


def _fail(exc: StateError) -> None:
    console.print(f"[red]{exc}[/red]")
    raise typer.Exit(1)


def _print_result(
    agent: str,
    action: str,
    stack: list[Any],
    created: bool,
    json_output: bool,
    human_message: str,
) -> None:
    if json_output:
        _print_json(_stack_payload(agent, action, stack, created))
        return
    console.print(human_message)


def _stack_payload(agent: str, action: str, stack: list[Any], created: bool) -> dict[str, Any]:
    return {
        "status": "ok",
        "action": action,
        "agent": agent,
        "created": created,
        "stack_depth": len(stack),
        "current": stack[-1].title if stack else None,
        "stack": [item.to_dict() for item in stack],
    }


def _print_json(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    app()
