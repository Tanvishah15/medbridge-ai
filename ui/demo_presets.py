"""Step 215 — demo report presets for hackathon UI selector."""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "data" / "synthetic_reports"

SELECT_PLACEHOLDER = "— Select demo report —"


@dataclass(frozen=True)
class DemoPreset:
    label: str
    report_file: str
    symptoms: str
    language: str
    audience: str
    literacy_level: str
    description: str


DEMO_PRESETS: dict[str, DemoPreset] = {
    "ENT — Otitis Media (rpt_ent_001)": DemoPreset(
        label="ENT — Otitis Media (rpt_ent_001)",
        report_file="rpt_ent_001.txt",
        symptoms="Mere kaan mein 3 din se ras aa rahi hai. Yeh report samjhao.",
        language="Hindi",
        audience="patient",
        literacy_level="simple",
        description="Demo 1 — Hindi patient, clarification loop",
    ),
    "Blood — Diabetes (rpt_blood_001)": DemoPreset(
        label="Blood — Diabetes (rpt_blood_001)",
        report_file="rpt_blood_001.txt",
        symptoms=(
            "Explain this blood test to my grandmother in Spanish. "
            "She is worried about the sugar numbers."
        ),
        language="Spanish",
        audience="family",
        literacy_level="simple",
        description="Demo 2 — Spanish family blood test summary",
    ),
    "MRI — Brain (rpt_mri_001)": DemoPreset(
        label="MRI — Brain (rpt_mri_001)",
        report_file="rpt_mri_001.txt",
        symptoms="لخص تقرير الرنين المغناطيسي لعائلتي",
        language="Arabic",
        audience="family",
        literacy_level="simple",
        description="Demo 3 — Arabic family MRI summary",
    ),
}


def list_demo_labels() -> list[str]:
    return [SELECT_PLACEHOLDER, *DEMO_PRESETS.keys()]


def get_demo_preset(label: str) -> DemoPreset | None:
    return DEMO_PRESETS.get(label)


def load_demo_report_text(label: str) -> str:
    preset = get_demo_preset(label)
    if preset is None:
        return ""
    path = REPORTS_DIR / preset.report_file
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
