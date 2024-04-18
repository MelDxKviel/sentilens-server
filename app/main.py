from fastapi import FastAPI
import nltk
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import note_router, user_router
from app.config import global_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_db()
    nltk.download('vader_lexicon')
    yield

app = FastAPI(
    title="Sentilens API",
    description="API for Sentilens app",
    version="0.1.2",
    lifespan=lifespan
)

app.include_router(note_router)
app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=global_settings.host, port=global_settings.port)
