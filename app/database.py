from sqlmodel import create_engine, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.models import *
from app.config import global_settings

DATABASE_URL = global_settings.psycopg_url.unicode_string()

engine = create_async_engine(DATABASE_URL, echo=True, future=True)


def init_db():
    SQLModel.metadata.create_all(engine)


async def get_session():
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    


if __name__ == "__main__":
    init_db()
