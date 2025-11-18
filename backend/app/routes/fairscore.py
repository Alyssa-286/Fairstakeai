from fastapi import APIRouter
from pydantic import BaseModel

from ..models.fairscore_model import model
from ..explainers import shap_viz

router = APIRouter()


class FairScoreRequest(BaseModel):
    user_features: dict


class FairScoreResponse(BaseModel):
    fairscore: int
    explanations: list[dict]
    improvement_suggestions: list[str]


@router.post("/score", response_model=FairScoreResponse)
async def score_user(req: FairScoreRequest) -> FairScoreResponse:
    result = model.predict(req.user_features)
    explanation_payload = shap_viz.summarize_explanations(result.explanations)["explanations"]
    return FairScoreResponse(
        fairscore=result.score,
        explanations=explanation_payload,
        improvement_suggestions=result.suggestions,
    )

