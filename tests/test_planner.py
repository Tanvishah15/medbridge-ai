from agents.models import PatientContext, ReportStructure
from agents.utils import symptoms_are_complete
from orchestrator.planner import _rule_based_plan, plan_workflow


def test_rule_based_plan_needs_clarification():
    report = ReportStructure(diagnosis="Otitis Media", findings=["Middle ear fluid"])
    patient = PatientContext(symptoms="Ear discharge from my ear.", language="English")
    plan = _rule_based_plan(report, patient, clarification_answers=None)
    assert plan.needs_clarification is True
    assert len(plan.knowledge_queries) >= 1


def test_rule_based_plan_skips_clarification_when_complete():
    report = ReportStructure(diagnosis="Otitis Media", findings=["Middle ear fluid"])
    patient = PatientContext(
        symptoms="Ear pain 6/10 for 3 days, no fever, fluid leaking.",
        language="English",
    )
    plan = _rule_based_plan(report, patient, clarification_answers=None)
    assert plan.needs_clarification is False


def test_rule_based_plan_multilingual_for_hindi():
    report = ReportStructure(diagnosis="Type 2 Diabetes")
    patient = PatientContext(symptoms="Tired and thirsty.", language="Hindi")
    plan = _rule_based_plan(report, patient, clarification_answers=["No fever. Pain 2/10 for 2 weeks."])
    assert plan.use_multilingual is True
    assert symptoms_are_complete(patient.symptoms) is False
