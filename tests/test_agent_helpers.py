from agents.utils import (
    detect_ungrounded_drug_names,
    has_disclaimer,
    has_empathy_tone,
    symptoms_are_complete,
)


def test_symptoms_complete_when_all_present():
    text = "Ear pain 6/10 for 3 days, no fever."
    assert symptoms_are_complete(text) is True


def test_symptoms_incomplete_missing_fever():
    text = "Ear pain for 3 days."
    assert symptoms_are_complete(text) is False


def test_detect_ungrounded_drug_names():
    answer = "Take metformin 500mg daily."
    assert "metformin" in detect_ungrounded_drug_names(answer)


def test_no_drugs_in_clean_answer():
    answer = "Middle ear fluid can cause discharge during infection."
    assert detect_ungrounded_drug_names(answer) == []


def test_has_empathy_tone():
    assert has_empathy_tone("I understand this may feel worrying.") is True


def test_has_disclaimer():
    assert has_disclaimer("Please consult your doctor.") is True
