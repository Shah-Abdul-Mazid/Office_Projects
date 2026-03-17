from pydantic import BaseModel, Field

from app.models.enums import SpeakerRole


class GeneratedSegmentPayload(BaseModel):
    sequence_index: int
    speaker: SpeakerRole
    content: str
    word_count: int = Field(ge=1)


class GeneratedScriptPayload(BaseModel):
    title: str | None = None
    summary: str | None = None
    total_word_count: int = Field(ge=900, le=1500)
    segments: list[GeneratedSegmentPayload]


class StoredObject(BaseModel):
    bucket: str
    key: str
    public_url: str | None = None


class RenderedAudioPayload(BaseModel):
    voice_id: str
    mime_type: str
    size_bytes: int
    checksum_sha256: str
    storage: StoredObject
