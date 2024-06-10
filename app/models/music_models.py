import enum

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text


class MusicCategory(str, enum.Enum):
    AUDIOFILE = "AUDIOFILE"
    RADIO = "RADIO"
    
 
class MusicBase(SQLModel):
    title: str
    category: MusicCategory = Field(default=MusicCategory.AUDIOFILE)
    url: str = Field(sa_column=Column(Text), default=None)

   
class Music(MusicBase, table=True):
    id: int = Field(primary_key=True, nullable=False)

    
class MusicRead(MusicBase):
    id: int
