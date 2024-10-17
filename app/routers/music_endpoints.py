from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Music, MusicRead
from app.database import get_session


music_router = APIRouter(
    prefix="/music",
    tags=["Music"],
    responses={404: {"description": "Not found"}},
)


@music_router.get("/")
async def get_music_list(
    session: AsyncSession = Depends(get_session)
) -> list[MusicRead]:
    result = await session.exec(select(Music))
    music_list = result.all()
    return music_list


@music_router.get("/{music_id}")
async def get_music_by_id(
    music_id: int,
    session: AsyncSession = Depends(get_session)
) -> MusicRead:
    result = await session.exec(select(Music).where(Music.id == music_id))
    music = result.first()

    if not music:
        raise HTTPException(status_code=404, detail="Music not found")

    return music
