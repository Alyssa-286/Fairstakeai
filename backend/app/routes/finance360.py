from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..utils import sms_parser, feature_builder

router = APIRouter()


class SMSParseRequest(BaseModel):
    sms_text: str = Field(..., min_length=10)


class Finance360Response(BaseModel):
    transactions: list[dict]
    monthly_summary: dict
    financial_health_score: int
    nudges: list[str]
    unparsed_transactions: list[str]
    derived_features: dict


@router.post("/sms_parse", response_model=Finance360Response)
async def parse_sms(request: SMSParseRequest) -> Finance360Response:
    transactions, unparsed = sms_parser.parse_sms_block(request.sms_text)
    metrics = sms_parser.compute_financial_metrics(transactions)
    derived_features = feature_builder.transactions_to_features(transactions)
    return Finance360Response(
        transactions=transactions,
        monthly_summary=metrics["monthly_summary"],
        financial_health_score=metrics["financial_health_score"],
        nudges=metrics["nudges"],
        unparsed_transactions=unparsed,
        derived_features=derived_features,
    )

