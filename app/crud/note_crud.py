import uuid as uuid_pkg
from datetime import datetime
from typing import Sequence, Optional

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Note, NoteCreate, NoteOptional, Sentiment
from app.sentiment_analyzer import get_sentiment


async def get_notes(session: AsyncSession, user_id: int) -> Sequence[Note]:
    result = await session.exec(
        select(Note).where(Note.owner_id == user_id).order_by(Note.created_at)
    )

    notes = result.all()

    return notes


async def get_note(
    note_id: uuid_pkg.UUID,
    session: AsyncSession,
    user_id: int
) -> Note | None:
    result = await session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    )

    note = result.first()

    return note


async def create_note(
    note: NoteCreate,
    session: AsyncSession,
    user_id: int
) -> Note:

    result = await session.exec(
        select(Note).where(Note.uuid == note.uuid)
    )

    db_note = result.first()

    if db_note:
        raise HTTPException(status_code=400, detail="UUID already assigned")

    new_note = Note.model_validate(note)
    sentiment = await get_sentiment(note.content, session)
    new_note.sentiment_id = sentiment.id
    new_note.owner_id = user_id

    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)

    return new_note


async def delete_note(
    note_id: uuid_pkg.UUID,
    session: AsyncSession,
    user_id: int
) -> Optional[Note]:
    result = await session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    )

    note = result.first()

    if not note:
        return None

    await session.delete(note)
    await session.commit()
    return note


async def update_note(
    note_id: uuid_pkg.UUID,
    note: NoteCreate | NoteOptional,
    session: AsyncSession,
    user_id: int
) -> Optional[Note]:
    result = await session.exec(
        select(Note).where(Note.uuid == note_id).where(
            Note.owner_id == user_id)
    )

    db_note = result.first()

    if not db_note:
        return None

    old_sentiment = None
    if note.title:
        db_note.title = note.title
    if note.content and note.content != db_note.content:
        db_note.content = note.content

        result = await session.exec(
            select(Sentiment).where(Sentiment.id == db_note.sentiment_id)
        )
        old_sentiment = result.first()

        new_sentiment = await get_sentiment(db_note.content, session)
        db_note.sentiment_id = new_sentiment.id

    db_note.updated_at = datetime.now()

    session.add(db_note)
    await session.commit()
    await session.refresh(db_note)

    if old_sentiment:
        await session.delete(old_sentiment)
        await session.commit()

    return db_note
