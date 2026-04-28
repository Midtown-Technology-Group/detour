# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import StackItem, TransitionResult


class StateError(RuntimeError):
    pass


class DetourState:
    def __init__(self, path: Path, agent: str = "default") -> None:
        self.path = path
        self.agent = _normalize_agent(agent)

    def load(self) -> list[StackItem]:
        return self.load_all().get(self.agent, [])

    def load_all(self) -> dict[str, list[StackItem]]:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise StateError(f"State file is not valid JSON: {self.path}") from exc
        if not isinstance(data, dict):
            raise StateError(f"State file must contain a JSON object: {self.path}")
        if "agents" in data:
            agents = data["agents"]
            if not isinstance(agents, dict):
                raise StateError(f"State file agents field must be an object: {self.path}")
            return {
                _normalize_agent(name): _stack_from_payload(payload)
                for name, payload in agents.items()
            }
        return {"default": _stack_from_payload(data)}

    def save(self, stack: list[StackItem]) -> None:
        agents = self.load_all()
        if stack:
            agents[self.agent] = stack
        else:
            agents.pop(self.agent, None)
        self.save_all(agents)

    def save_all(self, agents: dict[str, list[StackItem]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "agents": {
                _normalize_agent(agent): {"stack": [item.to_dict() for item in stack]}
                for agent, stack in sorted(agents.items())
                if stack
            }
        }
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)

    def start(self, title: str, force: bool = False, key: str | None = None) -> TransitionResult:
        stack = self.load()
        if stack and key and len(stack) == 1 and stack[0].key == key:
            return TransitionResult(depth=0, created=False, item=stack[0])
        if stack and not force:
            raise StateError("A detour stack is already active. Use --force to replace it.")
        item = StackItem(title=title, key=key)
        self.save([item])
        return TransitionResult(depth=0, created=True, item=item)

    def push(self, title: str, key: str | None = None) -> TransitionResult:
        stack = self.load()
        if not stack:
            raise StateError("No active detour. Start one first.")
        if key and stack[-1].key == key:
            return TransitionResult(depth=len(stack) - 1, created=False, item=stack[-1])
        item = StackItem(title=title, key=key)
        stack.append(item)
        self.save(stack)
        return TransitionResult(depth=len(stack) - 1, created=True, item=item)

    def pop(self) -> StackItem:
        stack = self.load()
        if not stack:
            raise StateError("No active detour.")
        item = stack.pop()
        self.save(stack)
        return item

    def reset(self) -> None:
        self.save([])


def _stack_from_payload(payload: object) -> list[StackItem]:
    if not isinstance(payload, dict):
        raise StateError("State stack payload must be an object.")
    stack = payload.get("stack", [])
    if not isinstance(stack, list):
        raise StateError("State stack field must be a list.")
    return [StackItem.from_dict(item) for item in stack]


def _normalize_agent(agent: object) -> str:
    value = str(agent).strip()
    if not value:
        raise StateError("Agent name cannot be empty.")
    return value
