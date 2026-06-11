from ui.trace_panel import agent_icon, format_step_output


def test_agent_icon_known_agent():
    assert agent_icon("Planner") == "🗺️"
    assert agent_icon("Safety") == "🛡️"


def test_agent_icon_unknown_agent():
    assert agent_icon("UnknownAgent") == "🤖"


def test_format_step_output_dict():
    text = format_step_output({"safe": True, "issues": []})
    assert '"safe": true' in text
    assert '"issues"' in text


def test_format_step_output_string():
    assert format_step_output("Plain explanation text") == "Plain explanation text"
