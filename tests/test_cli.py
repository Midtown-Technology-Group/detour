import json
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


def test_cli_json_status_and_idempotency_key(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(tmp_path / "notes"))

    start = runner.invoke(app, ["start", "Fix deploy", "--json"])
    first = runner.invoke(
        app,
        ["into", "Refresh kubeconfig", "--key", "kubeconfig-refresh", "--json"],
    )
    second = runner.invoke(
        app,
        ["into", "Refresh kubeconfig", "--key", "kubeconfig-refresh", "--json"],
    )
    status = runner.invoke(app, ["status", "--json"])

    assert start.exit_code == 0, start.output
    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert status.exit_code == 0, status.output
    assert json.loads(start.output)["stack_depth"] == 1
    assert json.loads(first.output)["created"] is True
    assert json.loads(second.output)["created"] is False
    assert json.loads(status.output)["stack"] == [
        {
            "title": "Fix deploy",
            "started_at": json.loads(status.output)["stack"][0]["started_at"],
            "key": None,
        },
        {
            "title": "Refresh kubeconfig",
            "started_at": json.loads(status.output)["stack"][1]["started_at"],
            "key": "kubeconfig-refresh",
        },
    ]


def test_cli_event_command_accepts_structured_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(tmp_path / "notes"))

    result = runner.invoke(
        app,
        [
            "event",
            '{"type":"start","title":"Fix deploy","key":"deploy"}',
            "--json",
        ],
    )
    into = runner.invoke(
        app,
        [
            "event",
            '{"type":"into","title":"Refresh kubeconfig","key":"kubeconfig-refresh"}',
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert into.exit_code == 0, into.output
    assert json.loads(into.output)["current"] == "Refresh kubeconfig"


def test_cli_agent_environment_scopes_active_stack(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(tmp_path / "notes"))

    monkeypatch.setenv("DETOUR_AGENT", "alpha")
    alpha_start = runner.invoke(app, ["start", "Fix deploy", "--json"])

    monkeypatch.setenv("DETOUR_AGENT", "beta")
    beta_start = runner.invoke(app, ["start", "Write docs", "--json"])
    beta_status = runner.invoke(app, ["status", "--json"])

    monkeypatch.setenv("DETOUR_AGENT", "alpha")
    alpha_status = runner.invoke(app, ["status", "--json"])
    agents = runner.invoke(app, ["agents", "--json"])

    assert alpha_start.exit_code == 0, alpha_start.output
    assert beta_start.exit_code == 0, beta_start.output
    assert json.loads(beta_status.output)["agent"] == "beta"
    assert json.loads(beta_status.output)["current"] == "Write docs"
    assert json.loads(alpha_status.output)["agent"] == "alpha"
    assert json.loads(alpha_status.output)["current"] == "Fix deploy"
    assert json.loads(agents.output)["agents"] == {
        "alpha": {"stack_depth": 1, "current": "Fix deploy"},
        "beta": {"stack_depth": 1, "current": "Write docs"},
    }


def test_cli_agent_option_overrides_environment(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(tmp_path / "notes"))
    monkeypatch.setenv("DETOUR_AGENT", "env-agent")

    result = runner.invoke(app, ["--agent", "flag-agent", "start", "Fix deploy", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["agent"] == "flag-agent"
