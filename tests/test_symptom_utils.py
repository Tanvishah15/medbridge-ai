from agents.utils import is_vague_symptom_message, symptoms_are_complete


def test_vague_hinglish_not_feeling_well():
    assert is_vague_symptom_message("muje acha feel nhi hora") is True


def test_specific_ent_symptoms_not_vague():
    text = "Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao."
    assert is_vague_symptom_message(text) is False


def test_explain_report_only_is_vague():
    assert is_vague_symptom_message("Yeh report samjhao") is True


def test_symptoms_are_complete_unchanged():
    assert symptoms_are_complete("3 din se dard, bukhar hai, pain 5/10") is True
