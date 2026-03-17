from __future__ import annotations

import uuid
from pathlib import Path

import anyio
from gtts import gTTS
from pydantic import BaseModel

from app.config import settings
from app.schemas import Voice


class TTSResult(BaseModel):
    voice: Voice
    path: Path


def _choose_tld(voice: Voice) -> str:
    return settings.voice_tld_overrides.get(voice.value, "com")


def _render_sync(text: str, voice: Voice, target_path: Path) -> None:
    tts = gTTS(text=text, lang="en", tld=_choose_tld(voice), slow=False)
    tts.save(target_path.as_posix())


async def synthesize_voice(text: str, voice: Voice) -> TTSResult:
    target_path = settings.tts_output_dir / f"{voice.value}-{uuid.uuid4().hex}.mp3"
    await anyio.to_thread.run_sync(_render_sync, text, voice, target_path)
    return TTSResult(voice=voice, path=target_path)
