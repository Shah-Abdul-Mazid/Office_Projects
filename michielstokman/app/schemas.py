from __future__ import annotations

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field, constr


class Voice(str, Enum):
    guide = "guide"
    student = "student"


class StoryRequest(BaseModel):
    theme: constr(strip_whitespace=True, min_length=10) = Field(..., description="High-level theme for the episode")
    audience: constr(strip_whitespace=True, min_length=5) = Field(..., description="Target demographic or persona")
    mood: constr(strip_whitespace=True, min_length=3) = Field("calm", description="Desired emotional tone")
    focus: constr(strip_whitespace=True, min_length=3, max_length=80) | None = Field(None, description="Primary focus point (e.g., breath awareness)")
    pacing: constr(strip_whitespace=True, max_length=40) | None = Field(None, description="Pacing instructions (e.g., slow & steady)")
    language: constr(strip_whitespace=True, min_length=2, max_length=10) = Field("en", description="Language code for generation and TTS (for example en, es, fr, hi)")


class DialogueTurn(BaseModel):
    voice: Voice
    text: str


class StoryBatchRequest(StoryRequest):
    count: int = Field(3, ge=1, le=31, description="Number of unique episodes to generate for the library")
    include_audio: bool = Field(True, description="Render guide.mp3 and student.mp3 for each generated episode")


class StoryResponse(BaseModel):
    episode_id: str
    title: str
    episode_text: str
    guide_script: str
    student_script: str
    dialogue: List[DialogueTurn]
    word_count: int
    language: str
    model: str
    episode_dir: str
    guidance_audio: Dict[Voice, str] = Field(..., description="Sample file paths for each voice when available")


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=200, description="Story or meditation script to narrate")
    voice: Voice = Field(Voice.guide, description="Narrating voice to render")
    language: constr(strip_whitespace=True, min_length=2, max_length=10) = Field("en", description="Language code for the narrator voice")
    audio_format: str = Field("mp3", description="Desired audio output. Use mp3 or an ElevenLabs mp3 output format like mp3_44100_128.")
    episode_id: str | None = Field(None, description="Optional episode id to store the track inside an existing episode folder")


class TTSResponse(BaseModel):
    voice: Voice
    audio_path: str
    episode_id: str | None = None


class EpisodeSummary(BaseModel):
    episode_id: str
    title: str
    language: str
    word_count: int
    episode_dir: str
    has_audio: bool


class BulkStoryResponse(BaseModel):
    episodes: List[StoryResponse]


class FeedbackRequest(BaseModel):
    episode_id: str
    rating: int = Field(..., ge=1, le=5, description="Simple quality score")
    platform: constr(strip_whitespace=True, min_length=2, max_length=40) | None = Field(None, description="Where the listener heard the content")
    notes: constr(strip_whitespace=True, min_length=3, max_length=500) | None = Field(None, description="Optional free-form feedback")


class FeedbackResponse(BaseModel):
    status: str


class OrchestrationResponse(BaseModel):
    story: StoryResponse
    rss_feed: str
    social_copy: Dict[str, str]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
