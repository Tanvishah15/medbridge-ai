from ui.grandmother_mode import GRANDMOTHER_SUFFIX, apply_grandmother_mode


def test_apply_grandmother_mode_sets_family_and_simple():
    mode = apply_grandmother_mode("She is worried about the sugar numbers.")
    assert mode["audience"] == "family"
    assert mode["literacy_level"] == "simple"
    assert GRANDMOTHER_SUFFIX in mode["symptoms"]
    assert "She is worried about the sugar numbers." in mode["symptoms"]


def test_apply_grandmother_mode_adds_space_after_punctuation():
    mode = apply_grandmother_mode("Yeh report samjhao.")
    assert mode["symptoms"] == f"Yeh report samjhao. {GRANDMOTHER_SUFFIX}"


def test_apply_grandmother_mode_does_not_duplicate_grandmother_phrase():
    original = "Explain this blood test to my grandmother in Spanish."
    mode = apply_grandmother_mode(original)
    assert mode["symptoms"] == original


def test_apply_grandmother_mode_empty_symptoms():
    mode = apply_grandmother_mode("")
    assert mode["symptoms"] == GRANDMOTHER_SUFFIX
