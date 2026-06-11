from ui.demo_presets import (
    DEMO_PRESETS,
    SELECT_PLACEHOLDER,
    get_demo_preset,
    list_demo_labels,
    load_demo_report_text,
)


def test_list_demo_labels_includes_all_three_demos():
    labels = list_demo_labels()
    assert labels[0] == SELECT_PLACEHOLDER
    assert len(DEMO_PRESETS) == 3
    for label in DEMO_PRESETS:
        assert label in labels


def test_load_ent_demo_report():
    text = load_demo_report_text("ENT — Otitis Media (rpt_ent_001)")
    assert "Otitis Media" in text
    assert "SYNTHETIC" in text


def test_load_blood_demo_report():
    text = load_demo_report_text("Blood — Diabetes (rpt_blood_001)")
    assert "SYNTHETIC" in text
    assert "glucose" in text.lower() or "diabetes" in text.lower()


def test_load_mri_demo_report():
    text = load_demo_report_text("MRI — Brain (rpt_mri_001)")
    assert "MRI" in text
    assert "microvascular" in text.lower() or "brain" in text.lower()


def test_demo_preset_has_symptoms_and_language():
    ent = get_demo_preset("ENT — Otitis Media (rpt_ent_001)")
    assert ent is not None
    assert ent.language == "Hindi"
    assert "kaan" in ent.symptoms.lower()

    blood = get_demo_preset("Blood — Diabetes (rpt_blood_001)")
    assert blood is not None
    assert blood.language == "Spanish"
    assert blood.audience == "family"

    mri = get_demo_preset("MRI — Brain (rpt_mri_001)")
    assert mri is not None
    assert mri.language == "Arabic"
