from typing import Literal
from pydantic import BaseModel, Field


ContentType = Literal['story', 'meditation']


class GenerateRequest(BaseModel):
    type: ContentType
    title: str
    growth_area: str
    life_phase: str
    minutes: int | None = 7
    voice: str = 'Guide'


class ModerationResult(BaseModel):
    approved: bool
    issues: list[str]


class TTSResult(BaseModel):
    status: str
    provider: str
    voice: str
    audio_url: str | None = None
    note: str | None = None


class GeneratedContent(BaseModel):
    title: str
    type: ContentType
    language: str = 'en'
    growth_area: str
    life_phase: str
    content: str
    moderation: ModerationResult
    tts: TTSResult
    created_at: str


class BatchRequest(BaseModel):
    month: str = Field(..., examples=['2026-03'])
    items: list[GenerateRequest]
