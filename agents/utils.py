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

MULTILINGUAL_DISCLAIMER_MARKERS = [
    "डॉक्टर",
    "चिकित्सक",
    "अस्वीकरण",
    "médico",
    "consulte",
    "aconsejo",
    "aviso",
    "طبيب",
    "استشر",
    "تنبيه",
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

BODY_PART_MARKERS = [
    "ear",
    "kaan",
    "blood",
    "glucose",
    "sugar",
    "mri",
    "brain",
    "heart",
    "chest",
    "diabetes",
    "cholesterol",
    "dard",
    "pain",
    "ras",
    "discharge",
]

VAGUE_SYMPTOM_PHRASES = [
    "not feeling well",
    "dont feel well",
    "don't feel well",
    "feel nhi",
    "acha feel nhi",
    "accha feel nhi",
    "theek nhi",
    "explain my report",
    "explain this report",
    "yeh report",
    "samjhao",
    "help me understand",
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


def is_vague_symptom_message(symptoms: str) -> bool:
    lower = symptoms.lower().strip()
    if not lower:
        return True
    has_body_part = any(marker in lower for marker in BODY_PART_MARKERS)
    if has_body_part and len(lower) >= 20:
        return False
    if any(phrase in lower for phrase in VAGUE_SYMPTOM_PHRASES):
        return not has_body_part
    return len(lower) < 20 and not has_body_part


def has_empathy_tone(text: str) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in EMPATHY_MARKERS)


def has_disclaimer(text: str) -> bool:
    lower = text.lower()
    if any(marker in lower for marker in DISCLAIMER_MARKERS):
        return True
    return any(marker in text for marker in MULTILINGUAL_DISCLAIMER_MARKERS)


def extract_citation_markers(text: str) -> list[str]:
    return re.findall(r"【[^】]+】", text)
