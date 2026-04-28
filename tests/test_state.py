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
