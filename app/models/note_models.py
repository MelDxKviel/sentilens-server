from datetime import datetime
from typing import Optional
import uuid as uuid_pkg

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ForeignKey, Integer

from .sentiment_models import Sentiment, SentimentRead


class NoteBase(SQLModel):
    title: str
    content: str


class Note(NoteBase, table=True):
    uuid: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True, index=True,
        nullable=False
    )
    owner_id: int = Field(default=None, sa_column=Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    sentiment_id: int = Field(default=None, foreign_key="sentiment.id")
    sentiment: Sentiment = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class NoteRead(NoteBase):
    uuid: uuid_pkg.UUID
    created_at: datetime
    updated_at: datetime

    sentiment: SentimentRead = None


class NoteCreate(NoteBase, SQLModel):
    uuid: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )


class NoteOptional(NoteBase):
    uuid: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str | None = None
    content: str | None = None
