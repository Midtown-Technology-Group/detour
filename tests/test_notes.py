from datetime import datetime
from pathlib import Path

from detour.notes import append_event


def test_creates_daily_note_with_section(tmp_path: Path) -> None:
    append_event(
        notes_dir=tmp_path,
        section_heading="## Detours",
        when=datetime(2026, 4, 28, 9, 12),
        time_format="%H:%M",
        depth=0,
        action="started",
        message="Fix deploy",
    )

    note = tmp_path / "2026-04-28.md"
    assert note.read_text(encoding="utf-8") == (
        "## Detours\n\n"
        "- 09:12 started: Fix deploy\n"
    )


def test_inserts_section_preserving_existing_content(tmp_path: Path) -> None:
    note = tmp_path / "2026-04-28.md"
    note.write_text("# Daily\n\nExisting note.\n", encoding="utf-8")

    append_event(
        notes_dir=tmp_path,
        section_heading="## Detours",
        when=datetime(2026, 4, 28, 9, 16),
        time_format="%H:%M",
        depth=1,
        action="detour",
        message="Refresh kubeconfig",
    )

    assert note.read_text(encoding="utf-8") == (
        "# Daily\n\n"
        "Existing note.\n\n"
        "## Detours\n\n"
        "  - 09:16 detour: Refresh kubeconfig\n"
    )


def test_appends_nested_events_with_correct_indentation(tmp_path: Path) -> None:
    when = datetime(2026, 4, 28, 9, 12)
    append_event(tmp_path, "## Detours", when, "%H:%M", 0, "started", "Fix deploy")
    append_event(
        tmp_path,
        "## Detours",
        when.replace(hour=9, minute=16),
        "%H:%M",
        1,
        "detour",
        "Refresh kubeconfig",
    )
    append_event(
        tmp_path,
        "## Detours",
        when.replace(hour=9, minute=18),
        "%H:%M",
        2,
        "detour",
        "Debug SSO role",
    )
    append_event(
        tmp_path,
        "## Detours",
        when.replace(hour=9, minute=24),
        "%H:%M",
        2,
        "done",
        "Role expired",
    )

    assert (tmp_path / "2026-04-28.md").read_text(encoding="utf-8") == (
        "## Detours\n\n"
        "- 09:12 started: Fix deploy\n"
        "  - 09:16 detour: Refresh kubeconfig\n"
        "    - 09:18 detour: Debug SSO role\n"
        "    - 09:24 done: Role expired\n"
    )
