from ui.safety_indicator import (
    render_safety_indicator,
    safety_status_icon,
    safety_status_label,
)


def test_safety_status_label_passed():
    assert safety_status_label(True) == "Safety validated"


def test_safety_status_label_failed():
    assert safety_status_label(False) == "Response adjusted for safety"


def test_safety_status_icon():
    assert safety_status_icon(True) == "✅"
    assert safety_status_icon(False) == "⚠️"
