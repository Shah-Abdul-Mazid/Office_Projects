from __future__ import annotations

import uuid
from pathlib import Path

import edge_tts
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.schemas import Voice
from app.services.library import build_episode_audio_path


class TTSResult(BaseModel):
    voice: Voice
    path: Path


async def synthesize_voice(
    text: str,
    voice: Voice,
    language: str = "en",
    episode_id: str | None = None,
    audio_format: str = "mp3",
) -> TTSResult:
    # Resolve the voice name from settings
    voice_name = settings.edge_tts_voices.get(voice.value, "en-US-GuyNeural")
    
    # In edge-tts, language is part of the voice name usually, 
    # but we can try to filter if needed. For now, we'll use the mapped defaults.
    
    target_path = build_episode_audio_path(episode_id, voice) if episode_id else \
                  settings.tts_output_dir / f"{voice.value}-{uuid.uuid4().hex}.mp3"

    try:
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(str(target_path))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Edge TTS generation failed: {str(exc)}",
        ) from exc

    return TTSResult(voice=voice, path=target_path)
