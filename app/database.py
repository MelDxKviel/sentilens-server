from sqlmodel import create_engine, SQLModel, Session

from app.models import *
from app.config import global_settings

DATABASE_URL = global_settings.psycopg_url.unicode_string()

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    init_db()
