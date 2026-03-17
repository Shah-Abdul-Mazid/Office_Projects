from __future__ import annotations

import asyncio
import csv
import datetime
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

from fastapi import HTTPException

from app.config import settings
from app.schemas import StoryRequest, StoryResponse, Voice
from app.services.ai_story import generate_episode, sanitize_episode_text
from app.services.tts import synthesize_voice, TTSResult


def _ensure_rss_file() -> None:
    path = settings.rss_feed_path
    if path.exists():
        return
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "AI Story & Meditation Studio"
    ET.SubElement(channel, "link").text = "https://example.com"
    ET.SubElement(channel, "description").text = "Daily guided stories"
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _append_rss(story: StoryResponse, audio_urls: Dict[Voice, str]) -> str:
    _ensure_rss_file()
    path = settings.rss_feed_path
    tree = ET.parse(path)
    channel = tree.getroot().find("channel")
    if channel is None:
        raise HTTPException(status_code=500, detail="RSS feed is malformed")
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = story.title
    ET.SubElement(item, "description").text = story.episode_text[:280]
    ET.SubElement(item, "pubDate").text = datetime.datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )
    for voice, url in audio_urls.items():
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", url)
        enclosure.set("type", "audio/mpeg")
        enclosure.set("role", voice.value)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return str(path)


def _log_feedback(story: StoryResponse, mood: str, voices: Dict[Voice, TTSResult]) -> None:
    csv_path = settings.feedback_log_path
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if not exists:
            writer.writerow(["timestamp", "title", "mood", "guide_ready", "student_ready"])
        writer.writerow(
            [
                datetime.datetime.utcnow().isoformat(),
                story.title,
                mood,
                str(voices.get(Voice.guide, "")),
                str(voices.get(Voice.student, "")),
            ]
        )


def _build_social_copy(story: StoryResponse) -> Dict[str, str]:
    summary = story.episode_text.replace("\n", " ")[:180].strip()
    caption = f"{story.title} — {summary}... Listen now via our RSS feed."
    return {"facebook": caption, "instagram": caption}


async def orchestrate_story(request: StoryRequest, client: object) -> Dict[str, object]:
    story = await generate_episode(request, client)
    cleaned_text = sanitize_episode_text(story.episode_text)
    tasks = [synthesize_voice(cleaned_text, voice) for voice in Voice]
    results = await asyncio.gather(*tasks)
    voice_lookup = {result.voice: result for result in results}
    story.guidance_audio = {voice: str(result.path) for voice, result in voice_lookup.items()}
    rss_path = _append_rss(story, story.guidance_audio)
    _log_feedback(story, request.mood, voice_lookup)
    socials = _build_social_copy(story)
    return {"story": story, "rss_feed": rss_path, "social_copy": socials}
