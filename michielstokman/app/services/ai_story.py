from __future__ import annotations

import re
import textwrap
from typing import Dict, Any

from fastapi import HTTPException, status
from openai import OpenAI

from app.config import settings
from app.schemas import StoryRequest, StoryResponse, Voice


def _build_prompt(request: StoryRequest) -> str:
    focus_clause = f"Focus on:{request.focus}." if request.focus else ""
    pacing_clause = f"Pacing: {request.pacing}." if request.pacing else ""
    instructions = textwrap.dedent(
        f"""
        You are a therapeutic storyteller and meditation guide writing a single episode of {request.theme} for {request.audience}.
        Tone: {request.mood}. {focus_clause} {pacing_clause}
        Deliver a story and meditation script that runs between {settings.min_story_words} and {settings.max_story_words} words.
        Break it into clearly labeled sections (Introduction, Journey, Reflection, Close) and keep narration calm and descriptive.
        Also provide two brief cues (one labeled GUIDE and one labeled STUDENT) with sample phonetic prompts for multi-voice narration (Guide = confident, Student = curious).
        """
    )
    return instructions


def _extract_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text.strip()

    for item in getattr(response, "output", []):
        for block in getattr(item, "content", []):
            if getattr(block, "type", "") == "output_text":
                return getattr(block, "text", "").strip()
    return ""


def _count_words(body: str) -> int:
    return len([token for token in body.split() if token.strip()])


def _sanitize_for_tts(text: str) -> str:
    cleaned = re.sub(r"(?m)^#{1,6}\s*", "", text)
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\[(Guide|Student)\]", r"\1", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\*\([^)]*\)\*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def sanitize_episode_text(text: str) -> str:
    """Prepare a generated episode for clean narration."""
    return _sanitize_for_tts(text)


async def generate_episode(request: StoryRequest, client: OpenAI) -> StoryResponse:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="OPENAI_API_KEY is missing. Set it in your environment before requesting story generation.",
        )

    prompt = _build_prompt(request)

    try:
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.95,
        )
    except Exception as exc:  # pragma: no cover - external service
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    episode_text = _extract_text(response)
    if not episode_text:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail="OpenAI returned an empty response")

    word_count = _count_words(episode_text)

    guidance_audio: Dict[Voice, str] = {
        Voice.guide: "pending",
        Voice.student: "pending",
    }

    return StoryResponse(
        title=request.theme,
        episode_text=episode_text,
        word_count=word_count,
        model=settings.openai_model,
        guidance_audio=guidance_audio,
    )
