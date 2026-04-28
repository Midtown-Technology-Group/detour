# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

import json
import os
from pathlib import Path

from .models import StackItem


class StateError(RuntimeError):
    pass


class DetourState:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[StackItem]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [StackItem.from_dict(item) for item in data.get("stack", [])]

    def save(self, stack: list[StackItem]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"stack": [item.to_dict() for item in stack]}
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)

    def start(self, title: str, force: bool = False) -> None:
        stack = self.load()
        if stack and not force:
            raise StateError("A detour stack is already active. Use --force to replace it.")
        self.save([StackItem(title=title)])

    def push(self, title: str) -> int:
        stack = self.load()
        if not stack:
            raise StateError("No active detour. Start one first.")
        stack.append(StackItem(title=title))
        self.save(stack)
        return len(stack) - 1

    def pop(self) -> StackItem:
        stack = self.load()
        if not stack:
            raise StateError("No active detour.")
        item = stack.pop()
        self.save(stack)
        return item

    def reset(self) -> None:
        self.save([])
