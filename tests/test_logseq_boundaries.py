import json
from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from detour.cli import app
from detour.notes import append_event


@pytest.mark.parametrize(
    "text",
    ["- Detours", "- Detours\n\t- Existing event", "- Detours\n  - Existing event"],
)
def test_logseq_event_starts_new_line_at_unterminated_eof(tmp_path: Path, text: str) -> None:
    note = tmp_path / "2026-04-28.md"
    note.write_text(text, encoding="utf-8")

    append_event(
        tmp_path,
        "Detours",
        datetime(2026, 4, 28, 9, 12),
        "%H:%M",
        0,
        "started",
        "Fix deploy",
        note_style="logseq",
    )

    assert note.read_text(encoding="utf-8") == text + "\n\t- 09:12 started: Fix deploy\n"


@pytest.mark.parametrize("indent", ["\t", "  "])
@pytest.mark.parametrize("has_root_section", [False, True])
def test_logseq_nested_heading_is_not_the_root_section(
    tmp_path: Path,
    indent: str,
    has_root_section: bool,
) -> None:
    unrelated = f"- Project notes\n{indent}- Detours\n{indent}\t- Keep this child\n"
    root_section = "- Detours\n\t- Existing event\n" if has_root_section else ""
    text = unrelated + root_section + "- Later human block\n"
    note = tmp_path / "2026-04-28.md"
    note.write_text(text, encoding="utf-8")

    append_event(
        tmp_path,
        "Detours",
        datetime(2026, 4, 28, 9, 12),
        "%H:%M",
        0,
        "started",
        "Fix deploy",
        note_style="logseq",
    )

    event = "\t- 09:12 started: Fix deploy\n"
    expected = (
        unrelated + root_section + event + "- Later human block\n"
        if has_root_section
        else text + "- Detours\n" + event
    )
    assert note.read_text(encoding="utf-8") == expected


@pytest.mark.parametrize(
    "text, expected_prefix",
    [
        ("- Detours", "- Detours\n"),
        (
            "- Project notes\n\t- Detours\n\t\t- Keep this child\n",
            "- Project notes\n\t- Detours\n\t\t- Keep this child\n- Detours\n",
        ),
    ],
)
def test_cli_start_preserves_logseq_block_boundaries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    text: str,
    expected_prefix: str,
) -> None:
    config_dir = tmp_path / "config"
    notes_dir = tmp_path / "notes"
    config_dir.mkdir()
    notes_dir.mkdir()
    (config_dir / "config.toml").write_text(
        'note_style = "logseq"\nsection_heading = "Detours"\n', encoding="utf-8"
    )
    monkeypatch.setenv("DETOUR_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("DETOUR_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("DETOUR_NOTES_DIR", str(notes_dir))
    monkeypatch.delenv("DETOUR_AGENT", raising=False)
    note = notes_dir / f"{datetime.now():%Y-%m-%d}.md"
    note.write_text(text, encoding="utf-8")

    result = CliRunner().invoke(app, ["start", "Fix deploy", "--json"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["current"] == "Fix deploy"
    updated = note.read_text(encoding="utf-8")
    assert updated.startswith(expected_prefix + "\t- ")
    assert updated.endswith(" started: Fix deploy\n")
