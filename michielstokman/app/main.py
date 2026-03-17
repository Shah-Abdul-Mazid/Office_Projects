from __future__ import annotations

import asyncio
from functools import lru_cache
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from openai import OpenAI

from app.config import settings
from app.schemas import (
    OrchestrationResponse,
    StoryRequest,
    StoryResponse,
    TTSRequest,
    TTSResponse,
    Voice,
)
from app.services.ai_story import generate_episode, sanitize_episode_text
from app.services.orchestrator import orchestrate_story
from app.services.tts import synthesize_voice, TTSResult


app = FastAPI(
    title="AI Story & Meditation Studio",
    version="0.1.0",
    description="Generate long-form episodes and multi-voice narration with FastAPI and OpenAI",
)


@lru_cache()
def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="OPENAI_API_KEY must be configured before requesting content.",
        )
    return OpenAI(api_key=settings.openai_api_key)


@app.post("/stories", response_model=StoryResponse)
async def create_episode(
    request: StoryRequest, client: OpenAI = Depends(get_openai_client)
) -> StoryResponse:
    return await generate_episode(request, client)


@app.post("/stories/full", response_model=StoryResponse)
async def create_episode_with_narration(
    request: StoryRequest, client: OpenAI = Depends(get_openai_client)
) -> StoryResponse:
    story = await generate_episode(request, client)
    cleaned_text = sanitize_episode_text(story.episode_text)
    tts_tasks = [synthesize_voice(cleaned_text, voice) for voice in Voice]
    tts_results = await asyncio.gather(*tts_tasks)
    story.guidance_audio = {result.voice: str(result.path) for result in tts_results}
    return story


@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_release(
    request: StoryRequest, client: OpenAI = Depends(get_openai_client)
) -> OrchestrationResponse:
    payload = await orchestrate_story(request, client)
    return OrchestrationResponse(**payload)

@app.post("/stories/tts", response_model=TTSResponse)
async def narrate_story(payload: TTSRequest) -> TTSResponse:
    result: TTSResult = await synthesize_voice(payload.text, payload.voice)
    return TTSResponse(voice=result.voice, audio_path=str(result.path))


@app.get("/audio/{file_name}")
async def fetch_audio(file_name: str) -> FileResponse:
    target_file = settings.tts_output_dir / Path(file_name).name
    if not target_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested audio file is missing"
        )
    return FileResponse(target_file, media_type="audio/mpeg", filename=target_file.name)
