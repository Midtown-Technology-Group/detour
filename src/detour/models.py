# Copyright (C) 2026 Midtown Technology Group LLC.
# SPDX-License-Identifier: AGPL-3.0-only

from __future__ import annotations

from dataclasses import dataclass, field


def local_timestamp() -> str:
    from datetime import datetime

    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass(frozen=True)
class StackItem:
    title: str
    started_at: str = field(default_factory=local_timestamp, compare=False)
    key: str | None = field(default=None, compare=False)

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> StackItem:
        return cls(
            title=str(data["title"]),
            started_at=str(data.get("started_at") or local_timestamp()),
            key=data.get("key"),
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "title": self.title,
            "started_at": self.started_at,
            "key": self.key,
        }


@dataclass(frozen=True)
class TransitionResult:
    depth: int
    created: bool
    item: StackItem
