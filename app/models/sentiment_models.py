from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text


class SentimentBase(SQLModel):
    category: int = Field(default=2)
    value: float = Field(default=0.5)
    advice: str = Field(sa_column=Column(Text), default=None)
    

class Sentiment(SentimentBase, table=True):
    id: int = Field(primary_key=True, nullable=False)


class SentimentRead(SentimentBase):
    pass
    