from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.episode import EpisodeStatus


class EpisodeGenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    language: str = Field(default="English", min_length=2, max_length=50)


class EpisodeRead(BaseModel):
    id: UUID
    topic: str
    language: str
    status: EpisodeStatus
    audio_url: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
