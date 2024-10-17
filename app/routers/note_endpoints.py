import uuid as uuid_pkg

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession


from app import crud
from app.auth import AuthHandler
from app.database import get_session
from app.models import NoteRead, NoteCreate, NoteOptional


note_router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={404: {"description": "Not found"}},
)
auth_handler = AuthHandler()


@note_router.get("/", response_model=list[NoteRead])
async def get_notes(
    session: AsyncSession = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> list[NoteRead]:
    notes = await crud.get_notes(
        user_id=user_id,
        session=session
    )
    return notes


@note_router.get("/{note_id}", response_model=NoteRead)
async def get_note(
    note_id: uuid_pkg.UUID, session: AsyncSession = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    note = await crud.get_note(
        note_id=note_id,
        session=session,
        user_id=user_id
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@note_router.post("/", response_model=NoteRead)
async def create_note(
    note: NoteCreate, session: AsyncSession = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    note = await crud.create_note(note=note, session=session, user_id=user_id)

    return note


@note_router.delete("/{note_id}")
async def delete_note(
    note_id: uuid_pkg.UUID, session: AsyncSession = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> JSONResponse:
    note = await crud.delete_note(
        note_id=note_id,
        session=session,
        user_id=user_id
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return JSONResponse(
        status_code=204,
        content={"detail": "Note has been deleted"}
    )


@note_router.put("/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: uuid_pkg.UUID, note: NoteCreate,
    session: AsyncSession = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    note = await crud.update_note(
        note=note,
        note_id=note_id,
        session=session,
        user_id=user_id
    )

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@note_router.patch("/{note_id}", response_model=NoteRead)
async def update_note_partial(
    note_id: uuid_pkg.UUID,
    note: NoteOptional, session: AsyncSession = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    note = await crud.update_note(
        note=note,
        note_id=note_id,
        session=session,
        user_id=user_id
    )

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note
