from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.episodes import router as episodes_router
from app.api.routes.rss import router as rss_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models import episode  # noqa: F401

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    settings.ensure_storage_dirs()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(episodes_router)
app.include_router(rss_router)
app.mount(
    "/media/audio",
    StaticFiles(directory=str(settings.local_audio_base_path)),
    name="audio_media",
)
