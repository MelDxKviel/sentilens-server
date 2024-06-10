from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.models import Recommendation, RecommendationRead
from app.database import get_session


reccomendation_router = APIRouter(
    prefix="/reccomendations",
    tags=["Reccomendations"],
    responses={404: {"description": "Not found"}},
)


@reccomendation_router.get("/")
async def get_reccomendations(session: Session = Depends(get_session)) -> list[RecommendationRead]:
    reccomendations = session.exec(select(Recommendation)).all()
    return reccomendations


@reccomendation_router.get("/{reccomendation_id}")
async def get_reccomendation_by_id(reccomendation_id: int, session: Session = Depends(get_session)) -> RecommendationRead:
    reccomendation = session.exec(select(Recommendation).where(
        Recommendation.id == reccomendation_id)
    ).first()
    if not reccomendation:
        raise HTTPException(status_code=404, detail="Reccomendation not found")
    return reccomendation
