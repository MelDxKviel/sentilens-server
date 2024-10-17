from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text


class RecommendationBase(SQLModel):
    title: str
    content: str = Field(sa_column=Column(Text), default=None)
    image: str
    url: str


class Recommendation(RecommendationBase, table=True):
    id: int = Field(primary_key=True, nullable=False)


class RecommendationRead(RecommendationBase):
    id: int
