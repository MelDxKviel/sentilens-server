from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Recommendation, RecommendationRead
from app.database import get_session


recommendation_router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
    responses={404: {"description": "Not found"}},
)


@recommendation_router.get("/")
async def get_recommendations(
    session: AsyncSession = Depends(get_session)
) -> list[RecommendationRead]:
    result = await session.exec(select(Recommendation))
    recommendations = result.all()
    return recommendations


@recommendation_router.get("/{recommendation_id}")
async def get_recommendation_by_id(
    recommendation_id: int,
    session: AsyncSession = Depends(get_session)
) -> RecommendationRead:
    result = await session.exec(select(Recommendation).where(
        Recommendation.id == recommendation_id)
    )

    recommendation = result.first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Reccomendation not found")

    return recommendation
