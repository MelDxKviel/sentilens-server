import uuid as uuid_pkg

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session


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
async def get_notes(session: Session = Depends(get_session),
                    user_id=Depends(auth_handler.auth_access_wrapper)) -> list[NoteRead]:
    notes = crud.get_notes(session, user_id)
    return notes


@note_router.get("/{note_id}", response_model=NoteRead)
async def get_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                   user_id=Depends(auth_handler.auth_access_wrapper)) -> NoteRead:
    note = crud.get_note(note_id, session, user_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@note_router.post("/", response_model=NoteRead)
async def create_note(note: NoteCreate, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_access_wrapper)) -> NoteRead:
    note = crud.create_note(note, session, user_id)

    return note


@note_router.delete("/{note_id}")
async def delete_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    note = crud.delete_note(note_id, session, user_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return JSONResponse(status_code=204, content={"detail": "Note has been deleted"})


@note_router.put("/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: uuid_pkg.UUID, note: NoteCreate,
    session: Session = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    note = crud.update_note(note_id, note, session, user_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@note_router.patch("/{note_id}", response_model=NoteRead)
async def update_note_partial(
    note_id: uuid_pkg.UUID,
    note: NoteOptional, session: Session = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    note = crud.update_note(note_id, note, session, user_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note
