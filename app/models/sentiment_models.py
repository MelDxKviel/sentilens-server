import enum

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text


class MoodCategory(str, enum.Enum):
    TERRIBLE = "TERRIBLE"
    BAD = "BAD"
    NEUTRAL = "NEUTRAL"
    GOOD = "GOOD"
    AWESOME = "AWESOME"

class SentimentBase(SQLModel):
    category: MoodCategory = Field(default=MoodCategory.NEUTRAL)
    value: float = Field(default=0.5)
    advice: str = Field(sa_column=Column(Text), default=None)


class Sentiment(SentimentBase, table=True):
    id: int = Field(primary_key=True, nullable=False)


class SentimentRead(SentimentBase):
    pass
