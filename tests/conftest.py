from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic_reports"


@pytest.fixture
def ent_report() -> str:
    return (DATA_DIR / "rpt_ent_001.txt").read_text(encoding="utf-8")


@pytest.fixture
def blood_report() -> str:
    return (DATA_DIR / "rpt_blood_001.txt").read_text(encoding="utf-8")


@pytest.fixture
def mri_report() -> str:
    return (DATA_DIR / "rpt_mri_001.txt").read_text(encoding="utf-8")
