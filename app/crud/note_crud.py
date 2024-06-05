import uuid as uuid_pkg
from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from app.models import Note, NoteCreate, Sentiment
from app.sentiment_analyzer import get_sentiment


def get_notes(session: Session, user_id: int) -> list[Note]:
    notes = session.exec(
        select(Note).where(Note.owner_id == user_id).order_by(Note.created_at)
    ).all()
    
    return notes

def get_note(note_id: uuid_pkg.UUID, session: Session, user_id: int) -> Note:
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    
    return note


def create_note(note: NoteCreate, session: Session, user_id: int) -> Note:
    
    db_note = session.exec(
        select(Note).where(Note.uuid == note.uuid)
    ).first()
    if db_note:
        raise HTTPException(status_code=400, detail="UUID already assigned")
    
    note = Note.model_validate(note)
    sentiment = get_sentiment(note.content, session)
    note.sentiment_id = sentiment.id
    note.owner_id = user_id

    try:
        session.add(note)
        session.commit()
        session.refresh(note)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Failed to create note")
    
    return note


def delete_note(note_id: uuid_pkg.UUID, session: Session, user_id: int) -> Note:
    note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    if not note:
        return None
    session.delete(note)
    session.commit()
    return note


def update_note(note_id: uuid_pkg.UUID, note: NoteCreate, session: Session, user_id: int) -> Note:
    db_note = session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    ).first()
    
    if not db_note:
        return None
    
    old_sentiment = None
    if note.title:
        db_note.title = note.title
    if note.content and note.content != db_note.content:
        db_note.content = note.content
        old_sentiment = session.exec(
            select(Sentiment).where(Sentiment.id == db_note.sentiment_id)
        ).first()

        new_sentiment = get_sentiment(db_note.content, session)
        db_note.sentiment_id = new_sentiment.id

    db_note.updated_at = datetime.now()

    session.add(db_note)
    session.commit()
    session.refresh(db_note)

    if old_sentiment:
        session.delete(old_sentiment)
        session.commit()
    
    return db_note
