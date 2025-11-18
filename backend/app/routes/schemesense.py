from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from ..utils import pdf_text_extractor, clause_segmenter, nlp_classifier

router = APIRouter()


class ClauseResponse(BaseModel):
    id: int
    text: str
    label: str
    confidence: float
    suggestion: str


class SchemeSenseResponse(BaseModel):
    fairness_score: int
    clauses: list[ClauseResponse]
    summary: str


@router.post("/upload", response_model=SchemeSenseResponse)
async def analyze_scheme(file: UploadFile = File(...)) -> SchemeSenseResponse:
    content = await file.read()
    text = pdf_text_extractor.extract_text_from_bytes(file.filename, content)
    clauses = clause_segmenter.segment_clauses(text)
    predictions = nlp_classifier.bulk_classify(clauses)
    clause_payload = []
    bias_count = 0
    for idx, (clause, pred) in enumerate(zip(clauses, predictions), start=1):
        if pred.label != "neutral":
            bias_count += 1
        clause_payload.append(
            ClauseResponse(
                id=idx,
                text=clause,
                label=pred.label,
                confidence=pred.confidence,
                suggestion=pred.suggestion,
            )
        )
    fairness_score = max(0, 100 - bias_count * 10)
    summary = "Detected potential exclusion clauses; consider the suggestions provided."
    return SchemeSenseResponse(fairness_score=fairness_score, clauses=clause_payload, summary=summary)

