from pydantic import BaseModel, Field

from app.models.enums import ScriptStatus, SpeakerRole
from app.schemas.audio import AudioAssetRead
from app.schemas.common import TimestampedReadModel
from app.schemas.job import PipelineJobRead


class SpeakerVoiceMap(BaseModel):
    guide_voice_id: str | None = None
    student_voice_id: str | None = None


class ScriptGenerationRequest(BaseModel):
    source_prompt: str = Field(..., min_length=20, max_length=4000)
    meditation_goal: str | None = Field(default=None, max_length=500)
    audience: str | None = Field(default=None, max_length=255)
    style_notes: str | None = Field(default=None, max_length=2000)
    title_hint: str | None = Field(default=None, max_length=255)
    language_code: str = Field(default="en-US", min_length=2, max_length=12)
    target_word_count: int = Field(default=1200, ge=900, le=1500)
    voice_map: SpeakerVoiceMap = Field(default_factory=SpeakerVoiceMap)


class ScriptSegmentRead(TimestampedReadModel):
    sequence_index: int
    speaker: SpeakerRole
    content: str
    word_count: int
    voice_id_override: str | None = None
    segment_metadata: dict


class StoryScriptRead(TimestampedReadModel):
    title: str | None = None
    source_prompt: str
    meditation_goal: str | None = None
    audience: str | None = None
    style_notes: str | None = None
    language_code: str
    target_word_count: int
    actual_word_count: int | None = None
    status: ScriptStatus
    provider: str
    model_name: str | None = None
    summary: str | None = None
    script_text: str | None = None
    structured_payload: dict | None = None
    voice_map: dict
    error_message: str | None = None
    segments: list[ScriptSegmentRead] = Field(default_factory=list)
    audio_assets: list[AudioAssetRead] = Field(default_factory=list)
    jobs: list[PipelineJobRead] = Field(default_factory=list)


class GenerationAcceptedResponse(BaseModel):
    script_id: str
    job_id: str
    status: ScriptStatus
