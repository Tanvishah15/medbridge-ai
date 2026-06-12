"""Step 233 — validate eval_cases.json structure (no Azure calls)."""

import json
from pathlib import Path

EVAL_FILE = Path(__file__).resolve().parent / "eval_cases.json"
REQUIRED_CASE_FIELDS = {"id", "name", "report_file", "patient", "expects"}
REQUIRED_PATIENT_FIELDS = {"symptoms", "language", "literacy_level", "audience"}
REPORT_FILES = {
    "rpt_ent_001.txt",
    "rpt_ent_002.txt",
    "rpt_blood_001.txt",
    "rpt_mri_001.txt",
}


def load_eval_cases() -> dict:
    return json.loads(EVAL_FILE.read_text(encoding="utf-8"))


def test_eval_cases_file_exists_and_has_ten_cases():
    data = load_eval_cases()
    assert data["meta"]["case_count"] == 10
    assert len(data["cases"]) == 10


def test_eval_cases_have_unique_ids():
    data = load_eval_cases()
    ids = [case["id"] for case in data["cases"]]
    assert len(ids) == len(set(ids))


def test_eval_cases_required_fields_and_reports():
    data = load_eval_cases()
    for case in data["cases"]:
        assert REQUIRED_CASE_FIELDS.issubset(case.keys())
        assert REQUIRED_PATIENT_FIELDS.issubset(case["patient"].keys())
        assert case["report_file"] in REPORT_FILES
        assert "criteria" in case["expects"] or case["expects"].get("clarification_needed") is not None


def test_eval_cases_cover_all_five_criteria():
    data = load_eval_cases()
    covered = set()
    for case in data["cases"]:
        criteria = case["expects"].get("criteria", {})
        covered.update(k for k, v in criteria.items() if v)
    assert covered == {
        "grounding",
        "safety",
        "multilingual",
        "clarification",
        "symptom_match",
    }


def test_eval_cases_include_demo_and_adversarial():
    data = load_eval_cases()
    ids = {case["id"] for case in data["cases"]}
    assert "eval_002" in ids
    assert "eval_003" in ids
    assert "eval_004" in ids
    assert any(case["id"].startswith("eval_008") for case in data["cases"])
    assert any("adversarial" in case["name"].lower() for case in data["cases"])
