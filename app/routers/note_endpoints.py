import uuid as uuid_pkg
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.auth import AuthHandler
from app.database import get_session
from app.models import Note, NoteRead, NoteCreate, Sentiment
from app.utils import get_sentiment

note_router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={404: {"description": "Not found"}},
)
auth_handler = AuthHandler()


@note_router.get("/", response_model=list[NoteRead])
async def get_notes(session: Session = Depends(get_session),
                    user_id=Depends(auth_handler.auth_access_wrapper)) -> list[NoteRead]:
    notes = session.exec(
        select(Note).where(Note.owner_id == user_id).order_by(Note.created_at)
    ).all()
    return notes


@note_router.get("/{note_id}", response_model=NoteRead)
async def get_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                   user_id=Depends(auth_handler.auth_access_wrapper)) -> NoteRead:
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


@note_router.post("/", response_model=NoteRead)
async def create_note(note: NoteCreate, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_access_wrapper)) -> NoteRead:

    db_note = Note.model_validate(note)
    sentiment = get_sentiment(db_note.content, session)
    db_note.sentiment_id = sentiment.id
    db_note.owner_id = user_id

    try:
        session.add(db_note)
        session.commit()
        session.refresh(db_note)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="UUID already assigned")

    return db_note


@note_router.delete("/{note_id}")
async def delete_note(note_id: uuid_pkg.UUID, session: Session = Depends(get_session),
                      user_id=Depends(auth_handler.auth_access_wrapper)) -> dict:
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return {"message": "Note has been deleted"}


@note_router.put("/{note_id}", response_model=NoteRead)
async def update_note(
    note_id: uuid_pkg.UUID, note: NoteCreate,
    session: Session = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    db_note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db_note.title = note.title
    db_note.content = note.content
    db_note.updated_at = datetime.now()

    old_sentiment = session.exec(
        select(Sentiment).where(Sentiment.id == db_note.sentiment_id)
    ).first()

    new_sentiment = get_sentiment(db_note.content, session)
    db_note.sentiment_id = new_sentiment.id

    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    session.delete(old_sentiment)
    session.commit()

    return db_note


@note_router.patch("/{note_id}", response_model=NoteRead)
async def update_note_partial(
    note_id: uuid_pkg.UUID,
    note: NoteCreate, session: Session = Depends(get_session),
    user_id=Depends(auth_handler.auth_access_wrapper)
) -> NoteRead:
    db_note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    old_sentiment = None
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.title:
        db_note.title = note.title
    if note.content:
        db_note.content = note.content
        old_sentiment = session.exec(
            select(Sentiment).where(Sentiment.id == db_note.sentiment_id)
        ).first()

        new_sentiment = get_sentiment(db_note.note, session)
        db_note.sentiment_id = new_sentiment.id

    db_note.updated_at = datetime.now()
    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    if old_sentiment:
        session.delete(old_sentiment)
        session.commit()
    return db_note
