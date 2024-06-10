from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.models import Recommendation, RecommendationRead
from app.database import get_session


recommendation_router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
    responses={404: {"description": "Not found"}},
)


@recommendation_router.get("/")
async def get_recommendations(session: Session = Depends(get_session)) -> list[RecommendationRead]:
    recommendations = session.exec(select(Recommendation)).all()
    return recommendations


@recommendation_router.get("/{recommendation_id}")
async def get_recommendation_by_id(recommendation_id: int, session: Session = Depends(get_session)) -> RecommendationRead:
    recommendation = session.exec(select(Recommendation).where(
        Recommendation.id == recommendation_id)
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Reccomendation not found")
    return recommendation
