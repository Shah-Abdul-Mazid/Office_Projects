from __future__ import annotations

import asyncio
import csv
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

from fastapi import HTTPException

from app.config import settings
from app.schemas import FeedbackRequest, StoryRequest, StoryResponse, Voice
from app.services.ai_story import generate_episode, sanitize_role_script
from app.services.library import build_audio_url, persist_story
from app.services.tts import TTSResult, synthesize_voice
from app.models import Feedback
from app.services.social import post_to_social_media, get_social_copy
from sqlalchemy.orm import Session


FEEDBACK_HEADERS = [
    "timestamp",
    "event_type",
    "episode_id",
    "title",
    "mood",
    "rating",
    "platform",
    "notes",
    "guide_audio",
    "student_audio",
]


def _ensure_rss_file() -> None:
    path = settings.rss_feed_path
    if path.exists():
        return
    
    # Register namespaces
    ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    
    root = ET.Element("rss", version="2.0")
    root.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "AI Story & Meditation Studio"
    ET.SubElement(channel, "link").text = settings.public_base_url
    ET.SubElement(channel, "description").text = "Daily guided stories and meditation episodes."
    ET.SubElement(channel, "language").text = "en-us"
    
    # Podcast Specific Tags
    itunes_author = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author")
    itunes_author.text = settings.podcast_author
    
    itunes_explicit = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit")
    itunes_explicit.text = settings.podcast_explicit

    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _append_rss(story: StoryResponse) -> str:
    _ensure_rss_file()
    path = settings.rss_feed_path
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    if channel is None:
        raise HTTPException(status_code=500, detail="RSS feed is malformed")

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = story.title
    ET.SubElement(item, "description").text = story.episode_text[:500] + "..."
    
    itunes_summary = ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}summary")
    itunes_summary.text = story.episode_text[:1000]

    ET.SubElement(item, "pubDate").text = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    ET.SubElement(item, "guid", isPermaLink="false").text = story.episode_id
    
    # Primary enclosure for Spotify
    enclosure = ET.SubElement(item, "enclosure")
    enclosure.set("url", build_audio_url(story.episode_id, Voice.guide))
    enclosure.set("type", "audio/mpeg")
    enclosure.set("length", "0")
    
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return str(path)


def append_feedback(payload: FeedbackRequest, db: Session) -> None:
    # Save to CSV (Legacy)
    csv_path = settings.feedback_log_path
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not exists:
            writer.writerow(FEEDBACK_HEADERS)
        writer.writerow(
            [
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "listener_feedback",
                payload.episode_id,
                "",
                "",
                payload.rating,
                payload.platform or "",
                payload.notes or "",
                "",
                "",
            ]
        )
    
    # Save to Database (New)
    db_feedback = Feedback(
        episode_id=payload.episode_id,
        rating=payload.rating,
        platform=payload.platform,
        notes=payload.notes
    )
    db.add(db_feedback)
    db.commit()


def _log_run_feedback(story: StoryResponse, mood: str, voices: Dict[Voice, TTSResult]) -> None:
    csv_path = settings.feedback_log_path
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not exists:
            writer.writerow(FEEDBACK_HEADERS)
        writer.writerow(
            [
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "pipeline_run",
                story.episode_id,
                story.title,
                mood,
                "",
                "",
                "",
                str(voices[Voice.guide].path),
                str(voices[Voice.student].path),
            ]
        )


def _build_social_copy(story: StoryResponse) -> Dict[str, str]:
    summary = story.episode_text.replace("\n", " ")[:180].strip()
    caption = f"{story.title} - {summary}... Listen now via our RSS feed."
    instagram = f"{story.title}\n\n{summary}...\n\n#meditation #mindfulness #aiaudio"
    return {"facebook": caption, "instagram": instagram}


async def attach_role_audio(story: StoryResponse, db: Session) -> StoryResponse:
    guide_text = sanitize_role_script(story.guide_script)
    student_text = sanitize_role_script(story.student_script)
    tasks = [
        synthesize_voice(guide_text, Voice.guide, language=story.language, episode_id=story.episode_id),
        synthesize_voice(student_text, Voice.student, language=story.language, episode_id=story.episode_id),
    ]
    results = await asyncio.gather(*tasks)
    voice_lookup = {result.voice: result for result in results}
    story.guidance_audio = {
        Voice.guide: str(voice_lookup[Voice.guide].path),
        Voice.student: str(voice_lookup[Voice.student].path),
    }
    return persist_story(story, db)


async def orchestrate_story(request: StoryRequest, client: object, db: Session) -> Dict[str, object]:
    story = await generate_episode(request, client, db)
    story = await attach_role_audio(story, db)
    voice_lookup = {
        Voice.guide: TTSResult(voice=Voice.guide, path=Path(story.guidance_audio[Voice.guide])),
        Voice.student: TTSResult(voice=Voice.student, path=Path(story.guidance_audio[Voice.student])),
    }
    rss_path = _append_rss(story)
    _log_run_feedback(story, request.mood, voice_lookup)
    
    social_copy = get_social_copy(story)
    social_results = await post_to_social_media(story)
    
    return {
        "story": story, 
        "rss_feed": rss_path, 
        "social_copy": social_copy,
        "social_automation_results": social_results
    }
