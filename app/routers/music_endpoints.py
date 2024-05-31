from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from app.models import Music, MusicRead
from app.database import get_session


music_router = APIRouter(
    prefix="/music",
    tags=["Music"],
    responses={404: {"description": "Not found"}},
)


@music_router.get("/")
async def get_music(session: Session = Depends(get_session)) -> list[MusicRead]:
    music_list = session.exec(select(Music)).all()
    return music_list
