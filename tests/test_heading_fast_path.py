from detour.notes import _ensure_section


def test_first_heading_in_large_note_preserves_all_content():
    text = "## Detours\n\n" + "- human note\n" * 10000
    assert _ensure_section(text, "## Detours") == text


def test_heading_with_embedded_line_separator_is_not_a_complete_line():
    for separator in "\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029":
        heading = "first" + separator + "second"
        text = heading + "\nbody"
        assert _ensure_section(text, heading) == text + "\n\n" + heading + "\n\n"


def test_heading_prefix_does_not_match_longer_line():
    text = "## Detours extra\n- human note\n"
    assert _ensure_section(text, "## Detours") == text.rstrip() + "\n\n## Detours\n\n"
