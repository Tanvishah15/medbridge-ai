import re

COMMON_DRUG_NAMES = [
    "metformin",
    "insulin",
    "aspirin",
    "ibuprofen",
    "amoxicillin",
    "atorvastatin",
    "lisinopril",
    "omeprazole",
    "prednisone",
    "acetaminophen",
    "paracetamol",
]

EMPATHY_MARKERS = [
    "understand",
    "sorry",
    "help",
    "feel",
    "worry",
    "concern",
    "here for you",
    "support",
]

DISCLAIMER_MARKERS = [
    "doctor",
    "healthcare",
    "medical advice",
    "consult",
    "professional",
    "not a substitute",
    "disclaimer",
    "educational",
]

DURATION_MARKERS = [
    "day",
    "days",
    "week",
    "weeks",
    "month",
    "months",
    "hour",
    "hours",
    "din",
    "haft",
    "since",
    "for 3",
    "for 2",
]

PAIN_MARKERS = [
    "pain",
    "dard",
    "/10",
    "mild",
    "moderate",
    "severe",
    "ache",
    "tender",
]

FEVER_MARKERS = [
    "fever",
    "bukhar",
    "temperature",
    "no fever",
    "without fever",
    "bina bukhar",
]


def detect_ungrounded_drug_names(answer: str) -> list[str]:
    lower = answer.lower()
    return [name for name in COMMON_DRUG_NAMES if name in lower]


def symptoms_are_complete(symptoms: str) -> bool:
    lower = symptoms.lower()
    has_duration = any(marker in lower for marker in DURATION_MARKERS)
    has_pain = any(marker in lower for marker in PAIN_MARKERS)
    has_fever = any(marker in lower for marker in FEVER_MARKERS)
    return has_duration and has_pain and has_fever


def has_empathy_tone(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in EMPATHY_MARKERS)


def has_disclaimer(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in DISCLAIMER_MARKERS)


def extract_citation_markers(text: str) -> list[str]:
    return re.findall(r"【[^】]+】", text)
