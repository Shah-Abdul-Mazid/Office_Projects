from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status

from app.config import settings
from app.schemas import EpisodeSummary, StoryResponse, Voice
from app.models import Episode
from sqlalchemy.orm import Session


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "episode"


def create_episode_id(title: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{_slugify(title)[:40]}-{uuid4().hex[:8]}"


def get_episode_dir(episode_id: str) -> Path:
    return settings.library_output_dir / Path(episode_id).name


def ensure_episode_dir(episode_id: str) -> Path:
    episode_dir = get_episode_dir(episode_id)
    episode_dir.mkdir(parents=True, exist_ok=True)
    return episode_dir


def build_episode_audio_path(episode_id: str, voice: Voice, audio_format: str = "mp3") -> Path:
    return ensure_episode_dir(episode_id) / f"{voice.value}.{audio_format}"


def build_audio_url(episode_id: str, voice: Voice, audio_format: str = "mp3") -> str:
    return f"{settings.public_base_url}/episodes/{episode_id}/audio/{voice.value}.{audio_format}"


def persist_story(story: StoryResponse, db: Session) -> StoryResponse:
    episode_dir = ensure_episode_dir(story.episode_id)
    (episode_dir / "episode.txt").write_text(story.episode_text, encoding="utf-8")
    (episode_dir / "guide.txt").write_text(story.guide_script, encoding="utf-8")
    (episode_dir / "student.txt").write_text(story.student_script, encoding="utf-8")
    (episode_dir / "metadata.json").write_text(
        json.dumps(story.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    
    # Save to database
    db_episode = Episode(
        id=story.episode_id,
        title=story.title,
        episode_text=story.episode_text,
        guide_script=story.guide_script,
        student_script=story.student_script,
        dialogue=[d.model_dump() for d in story.dialogue],
        word_count=story.word_count,
        language=story.language,
        model=story.model,
        episode_dir=story.episode_dir,
        guidance_audio={k.value: v for k, v in story.guidance_audio.items()},
    )
    db.merge(db_episode)
    db.commit()
    return story


def load_story(episode_id: str, db: Session) -> StoryResponse:
    db_episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not db_episode:
        # Fallback to file for existing data migration if needed, 
        # but primarily use DB now.
        metadata_path = get_episode_dir(episode_id) / "metadata.json"
        if not metadata_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Episode '{episode_id}' was not found.",
            )
        return StoryResponse.model_validate_json(metadata_path.read_text(encoding="utf-8"))
    
    return StoryResponse(
        episode_id=db_episode.id,
        title=db_episode.title,
        episode_text=db_episode.episode_text,
        guide_script=db_episode.guide_script,
        student_script=db_episode.student_script,
        dialogue=db_episode.dialogue,
        word_count=db_episode.word_count,
        language=db_episode.language,
        model=db_episode.model,
        episode_dir=db_episode.episode_dir,
        guidance_audio={Voice(k): v for k, v in db_episode.guidance_audio.items()}
    )


def list_episode_summaries(db: Session) -> list[EpisodeSummary]:
    db_episodes = db.query(Episode).order_by(Episode.created_at.desc()).all()
    summaries: list[EpisodeSummary] = []
    
    for ep in db_episodes:
        summaries.append(
            EpisodeSummary(
                episode_id=ep.id,
                title=ep.title,
                language=ep.language,
                word_count=ep.word_count,
                episode_dir=ep.episode_dir,
                has_audio=bool(ep.guidance_audio)
            )
        )
    
    # If DB is empty, maybe fallback to files for legacy support during transition
    if not summaries:
        for metadata_path in sorted(settings.library_output_dir.glob("*/metadata.json"), reverse=True):
            story = StoryResponse.model_validate_json(metadata_path.read_text(encoding="utf-8"))
            summaries.append(
                EpisodeSummary(
                    episode_id=story.episode_id,
                    title=story.title,
                    language=story.language,
                    word_count=story.word_count,
                    episode_dir=story.episode_dir,
                    has_audio=all(
                        story.guidance_audio.get(voice, "").endswith(f"{voice.value}.mp3")
                        for voice in Voice
                    ),
                )
            )
    return summaries
