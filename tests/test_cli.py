from pathlib import Path

from typer.testing import CliRunner

from detour.cli import app

runner = CliRunner()


def test_cli_smoke_workflow_uses_environment_overrides(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    state_dir = tmp_path / "state"
    notes_dir = tmp_path / "notes"
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(state_dir))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(notes_dir))

    result = runner.invoke(app, ["start", "Fix deploy"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(app, ["into", "Refresh kubeconfig"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(app, ["log", "kubectl context expired"])
    assert result.exit_code == 0, result.output

    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0, result.output
    assert "Fix deploy" in result.output
    assert "Refresh kubeconfig" in result.output

    result = runner.invoke(app, ["done", "Refreshed"])
    assert result.exit_code == 0, result.output

    note = next(notes_dir.glob("*.md"))
    text = note.read_text(encoding="utf-8")
    assert "started: Fix deploy" in text
    assert "detour: Refresh kubeconfig" in text
    assert "note: kubectl context expired" in text
    assert "done: Refreshed" in text


def test_done_and_back_on_empty_stack_are_cli_errors(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(tmp_path / "notes"))

    done = runner.invoke(app, ["done"])
    back = runner.invoke(app, ["back"])

    assert done.exit_code != 0
    assert back.exit_code != 0
    assert "No active detour" in done.output
    assert "No active detour" in back.output


def test_reset_requires_yes(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(tmp_path / "notes"))

    runner.invoke(app, ["start", "Fix deploy"])
    result = runner.invoke(app, ["reset"])

    assert result.exit_code != 0
    assert "Pass --yes" in result.output
