from ui.disclaimer_banner import DISCLAIMER_BANNER_TEXT


def test_disclaimer_banner_text_matches_playbook():
    assert DISCLAIMER_BANNER_TEXT == (
        "Demo only. Synthetic data. Not medical advice. Always consult your doctor."
    )
