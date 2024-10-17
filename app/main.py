from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    note_router,
    user_router,
    music_router,
    recommendation_router
)
from app.config import global_settings


origins = [
    "http://localhost:8080",
    "https://localhost:8080",
    "http://localhost",
    "https://localhost",
]

app = FastAPI(
    title="Sentilens API",
    description="API for Sentilens app",
    version="0.3.2",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(note_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(music_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=global_settings.host, port=global_settings.port)
