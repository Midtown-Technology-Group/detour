# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StackItem:
    title: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> StackItem:
        return cls(title=data["title"])

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title}
