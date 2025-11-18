from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from ..utils import pdf_text_extractor

router = APIRouter()

RISK_RULES = {
    "auto_renew": ["auto-renew", "automatic renewal"],
    "high_apr": ["apr", "interest rate"],
    "hidden_fees": ["processing fee", "penalty", "late fee"],
    "insurance_bundling": ["insurance bundled", "mandatory insurance"],
}


class RiskClause(BaseModel):
    text: str
    type: str
    recommendation: str


class LoanGuardResponse(BaseModel):
    risk_score: int
    risky_clauses: list[RiskClause]
    summary: str


def analyze_text(text: str) -> LoanGuardResponse:
    risky_clauses = []
    risk_score = 20
    for line in text.splitlines():
        lower_line = line.lower()
        for rule, keywords in RISK_RULES.items():
            if any(keyword in lower_line for keyword in keywords):
                risky_clauses.append(
                    RiskClause(
                        text=line.strip(),
                        type=rule,
                        recommendation="Clarify terms and provide opt-out.",
                    )
                )
                risk_score += 15
    bounded_risk = min(100, risk_score)
    summary = "High risk due to aggressive clauses." if risky_clauses else "Low risk detected."
    return LoanGuardResponse(risk_score=bounded_risk, risky_clauses=risky_clauses, summary=summary)


@router.post("/analyze", response_model=LoanGuardResponse)
async def analyze_loan(file: UploadFile = File(...)) -> LoanGuardResponse:
    content = await file.read()
    text = pdf_text_extractor.extract_text_from_bytes(file.filename, content)
    return analyze_text(text)

