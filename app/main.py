from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


origins = [
    "http://localhost:8080",
    "https://localhost:8080",
    "http://localhost",
    "https://localhost",
]

app = FastAPI(
    title="Sentilens API",
    description="API for Sentilens app",
    version="0.2.3",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    llow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(note_router, prefix="/api")
app.include_router(user_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=global_settings.host, port=global_settings.port)
