from ui.loading_steps import LOADING_STEPS, STEP_INDEX, format_step_chain, notify_progress


def test_loading_steps_match_playbook_order():
    labels = [step["label"] for step in LOADING_STEPS]
    assert labels == [
        "Reading report",
        "Checking symptoms",
        "Retrieving knowledge",
        "Explaining",
        "Validating safety",
    ]


def test_format_step_chain_highlights_active_step():
    chain = format_step_chain(2)
    assert "✅ Reading report" in chain
    assert "✅ Checking symptoms" in chain
    assert "**Retrieving knowledge...**" in chain
    assert "Explaining" in chain
    assert "→" in chain


def test_notify_progress_calls_callback():
    seen: list[str] = []

    def _cb(step: str) -> None:
        seen.append(step)

    notify_progress(_cb, "explaining")
    assert seen == ["explaining"]


def test_notify_progress_none_callback():
    notify_progress(None, "explaining")


def test_step_index_covers_all_keys():
    assert len(STEP_INDEX) == len(LOADING_STEPS)
