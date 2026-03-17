from __future__ import annotations

from enum import Enum
from typing import Dict

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


class StoryResponse(BaseModel):
    title: str
    episode_text: str
    word_count: int
    model: str
    guidance_audio: Dict[Voice, str] = Field(..., description="Sample file paths for each voice when available")


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=200, description="Story or meditation script to narrate")
    voice: Voice = Field(Voice.guide, description="Narrating voice to render")
    audio_format: str = Field("mp3", description="Desired audio container (mp3, wav)")


class TTSResponse(BaseModel):
    voice: Voice
    audio_path: str


class OrchestrationResponse(BaseModel):
    story: StoryResponse
    rss_feed: str
    social_copy: Dict[str, str]
