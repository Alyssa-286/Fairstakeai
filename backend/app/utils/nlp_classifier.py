from dataclasses import dataclass
from typing import List

BIAS_KEYWORDS = {
    "income_exclusion": ["salary slips", "minimum income", "cibil"],
    "gender_bias": ["only male", "only female"],
    "location_bias": ["urban residents", "metro cities only"],
}


@dataclass
class ClausePrediction:
    label: str
    confidence: float
    suggestion: str


SUGGESTIONS = {
    "income_exclusion": "Allow alternative proofs like bank inflows or gig statements.",
    "gender_bias": "Ensure eligibility is gender neutral.",
    "location_bias": "Provide rural/urban parity or alternative verification.",
}


def classify_clause(text: str) -> ClausePrediction:
    text_lower = text.lower()
    for label, keywords in BIAS_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return ClausePrediction(
                label=label,
                confidence=0.82,
                suggestion=SUGGESTIONS[label],
            )
    return ClausePrediction(
        label="neutral",
        confidence=0.4,
        suggestion="No action needed.",
    )


def bulk_classify(clauses: List[str]) -> List[ClausePrediction]:
    return [classify_clause(clause) for clause in clauses]

