from pathlib import Path

import pytest

from detour.models import StackItem
from detour.state import DetourState, StateError


def test_stack_push_pop_behavior(tmp_path: Path) -> None:
    state_path = tmp_path / "stack.json"
    state = DetourState(state_path)

    state.start("Fix deploy")
    state.push("Refresh kubeconfig")

    assert [item.title for item in state.load()] == ["Fix deploy", "Refresh kubeconfig"]
    assert state.pop().title == "Refresh kubeconfig"
    assert [item.title for item in state.load()] == ["Fix deploy"]


def test_stack_items_record_started_at_and_optional_key(tmp_path: Path) -> None:
    state = DetourState(tmp_path / "stack.json")

    state.start("Fix deploy", key="deploy")
    state.push("Refresh kubeconfig", key="kubeconfig-refresh")

    stack = state.load()
    assert stack[0].key == "deploy"
    assert stack[0].started_at
    assert stack[1].key == "kubeconfig-refresh"
    assert stack[1].started_at


def test_push_with_same_top_key_is_idempotent(tmp_path: Path) -> None:
    state = DetourState(tmp_path / "stack.json")
    state.start("Fix deploy")

    first = state.push("Refresh kubeconfig", key="kubeconfig-refresh")
    second = state.push("Refresh kubeconfig", key="kubeconfig-refresh")

    assert first.created is True
    assert second.created is False
    assert second.depth == 1
    assert [item.title for item in state.load()] == ["Fix deploy", "Refresh kubeconfig"]


def test_start_fails_when_stack_exists_unless_forced(tmp_path: Path) -> None:
    state = DetourState(tmp_path / "stack.json")
    state.start("Fix deploy")

    with pytest.raises(StateError, match="already active"):
        state.start("Other task")

    state.start("Other task", force=True)
    assert state.load() == [StackItem(title="Other task")]


def test_pop_empty_stack_errors(tmp_path: Path) -> None:
    state = DetourState(tmp_path / "stack.json")

    with pytest.raises(StateError, match="No active detour"):
        state.pop()
