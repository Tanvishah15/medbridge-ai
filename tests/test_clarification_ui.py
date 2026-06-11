from ui.clarification_ui import format_question


def test_format_question_plain_text():
    assert format_question("Kya aapko bukhar hai?") == "Kya aapko bukhar hai?"


def test_format_question_dict_string():
    raw = "{'question': 'Kya dard hai?'}"
    assert format_question(raw) == "Kya dard hai?"


def test_format_question_json_like_string():
    raw = '{"question": "Any fever?"}'
    assert format_question(raw) == "Any fever?"
