import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from pydub import AudioSegment

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.episode import Episode, EpisodeStatus
from app.services.exceptions import StorytellingServiceError
from app.services.openai_service import synthesize_speech_chunk
from app.services.storage import get_storage_service
from app.services.webhook import send_episode_webhook

settings = get_settings()
ROLE_VOICES = {"Guide": "onyx", "Student": "nova"}


def split_text_for_tts(text: str, chunk_size: int) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= chunk_size:
        return [cleaned]

    sentence_parts = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for sentence in sentence_parts:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > chunk_size:
            words = sentence.split()
            overflow: list[str] = []
            overflow_length = 0
            for word in words:
                projected = overflow_length + len(word) + (1 if overflow else 0)
                if projected > chunk_size:
                    chunks.append(" ".join(overflow))
                    overflow = [word]
                    overflow_length = len(word)
                else:
                    overflow.append(word)
                    overflow_length = projected
            if overflow:
                chunks.append(" ".join(overflow))
            continue

        projected = current_length + len(sentence) + (1 if current else 0)
        if projected > chunk_size:
            chunks.append(" ".join(current))
            current = [sentence]
            current_length = len(sentence)
        else:
            current.append(sentence)
            current_length = projected

    if current:
        chunks.append(" ".join(current))

    return [chunk for chunk in chunks if chunk]


def concatenate_audio_chunks(chunk_files: list[Path], destination: Path) -> Path:
    combined = AudioSegment.silent(duration=0)
    pause = AudioSegment.silent(duration=350)
    for chunk_file in chunk_files:
        combined += AudioSegment.from_file(chunk_file, format="mp3")
        combined += pause
    destination.parent.mkdir(parents=True, exist_ok=True)
    combined.export(destination, format="mp3", bitrate="192k")
    return destination


async def process_audio_pipeline(episode_id: UUID, script_json: list[dict[str, str]]) -> None:
    db = SessionLocal()
    chunk_files: list[Path] = []

    try:
        episode = db.get(Episode, episode_id)
        if episode is None:
            raise StorytellingServiceError(f"Episode {episode_id} was not found for audio processing.")

        for line_index, line in enumerate(script_json, start=1):
            role = line["role"]
            voice = ROLE_VOICES.get(role)
            if voice is None:
                raise StorytellingServiceError(f"Unsupported dialogue role: {role}")

            text_chunks = split_text_for_tts(line["text"], settings.tts_chunk_max_chars)
            for chunk_index, text_chunk in enumerate(text_chunks, start=1):
                chunk_path = settings.local_chunk_base_path / f"{episode_id}_{line_index:03d}_{chunk_index:02d}.mp3"
                await synthesize_speech_chunk(text=text_chunk, voice=voice, destination=chunk_path)
                chunk_files.append(chunk_path)

        if not chunk_files:
            raise StorytellingServiceError("No audio was produced from the generated script.")

        final_mix_path = settings.local_chunk_base_path / f"{episode_id}_final.mp3"
        await asyncio.to_thread(concatenate_audio_chunks, chunk_files, final_mix_path)

        stored_file = await asyncio.to_thread(
            get_storage_service().store_episode_audio,
            final_mix_path,
            episode_id,
        )

        episode.status = EpisodeStatus.COMPLETED
        episode.audio_url = stored_file.url
        episode.audio_storage_key = stored_file.storage_key
        episode.audio_size_bytes = stored_file.size_bytes
        episode.published_at = datetime.now(timezone.utc)
        episode.error_message = None
        db.add(episode)
        db.commit()
        db.refresh(episode)
    except Exception as exc:
        db.rollback()
        episode = db.get(Episode, episode_id)
        if episode is not None:
            episode.status = EpisodeStatus.FAILED
            episode.error_message = str(exc)
            db.add(episode)
            db.commit()
        raise
    else:
        try:
            await send_episode_webhook(episode)
            episode.webhook_notified = True
            db.add(episode)
            db.commit()
        except Exception as exc:
            db.rollback()
            episode = db.get(Episode, episode_id)
            if episode is not None:
                episode.error_message = f"Audio ready, but webhook notification failed: {exc}"
                db.add(episode)
                db.commit()
    finally:
        for path in chunk_files:
            path.unlink(missing_ok=True)
        temp_mix = settings.local_chunk_base_path / f"{episode_id}_final.mp3"
        temp_mix.unlink(missing_ok=True)
        db.close()


def run_audio_pipeline_task(episode_id: UUID, script_json: list[dict[str, str]]) -> None:
    asyncio.run(process_audio_pipeline(episode_id=episode_id, script_json=script_json))
