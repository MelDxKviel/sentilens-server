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
async def get_music_list(session: Session = Depends(get_session)) -> list[MusicRead]:
    music_list = session.exec(select(Music)).all()
    return music_list


@music_router.get("/{music_id}")
async def get_music_by_id(music_id: int, session: Session = Depends(get_session)) -> MusicRead:
    music = session.exec(select(Music).where(Music.id == music_id)).first()
    if not music:
        raise HTTPException(status_code=404, detail="Music not found")
    return music
