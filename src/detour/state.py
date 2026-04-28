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
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[StackItem]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise StateError(f"State file is not valid JSON: {self.path}") from exc
        return [StackItem.from_dict(item) for item in data.get("stack", [])]

    def save(self, stack: list[StackItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"stack": [item.to_dict() for item in stack]}
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
