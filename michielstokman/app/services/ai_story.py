from __future__ import annotations

import re
import textwrap
from typing import Any

from fastapi import HTTPException, status
from openai import OpenAI

from app.config import settings
from app.schemas import DialogueTurn, StoryRequest, StoryResponse, Voice
from app.services.library import create_episode_id, ensure_episode_dir, persist_story
from sqlalchemy.orm import Session


SECTION_PATTERN = re.compile(
    r"(?is)TITLE:\s*(?P<title>.*?)\s*FULL_EPISODE:\s*(?P<episode>.*?)\s*GUIDE_SCRIPT:\s*(?P<guide>.*?)\s*STUDENT_SCRIPT:\s*(?P<student>.*)"
)


def _build_prompt(request: StoryRequest) -> str:
    focus_clause = f"Focus point: {request.focus}." if request.focus else ""
    pacing_clause = f"Pacing: {request.pacing}." if request.pacing else ""
    return textwrap.dedent(
        f"""
        You are designing a premium meditation-learning episode in {request.language}.
        Theme: {request.theme}
        Audience: {request.audience}
        Mood: {request.mood}
        {focus_clause}
        {pacing_clause}

        Requirements:
        - Write a calm, useful episode between {settings.min_story_words} and {settings.max_story_words} words.
        - The episode must feel like a guided dialogue where the Guide asks reflective questions and the Student answers honestly.
        - Keep the long-form FULL_EPISODE suitable for RSS publishing with these labeled sections: Introduction, Journey, Reflection, Close.
        - Also provide a separate GUIDE_SCRIPT containing only the Guide's questions or prompts.
        - Provide a separate STUDENT_SCRIPT containing only the Student's answers.
        - GUIDE_SCRIPT and STUDENT_SCRIPT must have the same number of lines, ideally 8 to 12.
        - Keep each guide line concise enough for TTS, and each student line natural and specific.

        Return only plain text in exactly this template:
        TITLE:
        <short episode title>

        FULL_EPISODE:
        <the complete 900-1500 word episode>

        GUIDE_SCRIPT:
        1. <guide line>
        2. <guide line>

        STUDENT_SCRIPT:
        1. <student line>
        2. <student line>
        """
    ).strip()


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


def _clean_script_lines(script_block: str) -> list[str]:
    lines: list[str] = []
    for raw_line in script_block.splitlines():
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", raw_line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def _sanitize_for_tts(text: str) -> str:
    cleaned = re.sub(r"(?m)^#{1,6}\s*", "", text)
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\[(Guide|Student)\]", r"\1", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\*\([^)]*\)\*", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def sanitize_episode_text(text: str) -> str:
    return _sanitize_for_tts(text)


def sanitize_role_script(text: str) -> str:
    normalized = "\n".join(_clean_script_lines(text))
    return _sanitize_for_tts(normalized)


def _parse_story_payload(payload: str, fallback_title: str) -> tuple[str, str, str, str]:
    match = SECTION_PATTERN.search(payload)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The model response could not be parsed into title, episode, guide script, and student script.",
        )

    title = match.group("title").strip() or fallback_title
    episode_text = match.group("episode").strip()
    guide_lines = _clean_script_lines(match.group("guide"))
    student_lines = _clean_script_lines(match.group("student"))

    if not episode_text or not guide_lines or not student_lines:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The model response was missing the episode body or role scripts.",
        )

    pair_count = min(len(guide_lines), len(student_lines))
    guide_script = "\n".join(guide_lines[:pair_count])
    student_script = "\n".join(student_lines[:pair_count])
    return title, episode_text, guide_script, student_script


def _build_dialogue(guide_script: str, student_script: str) -> list[DialogueTurn]:
    guide_lines = _clean_script_lines(guide_script)
    student_lines = _clean_script_lines(student_script)
    turns: list[DialogueTurn] = []
    for guide_line, student_line in zip(guide_lines, student_lines):
        turns.append(DialogueTurn(voice=Voice.guide, text=guide_line))
        turns.append(DialogueTurn(voice=Voice.student, text=student_line))
    return turns


async def generate_episode(request: StoryRequest, client: OpenAI, db: Session) -> StoryResponse:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="OPENAI_API_KEY is missing. Set it in your environment before requesting story generation.",
        )

    # Note: Using V1 Chat Completion as standard for openai>=1.0.0
    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": _build_prompt(request)}],
            temperature=0.7,
            max_tokens=4000,
            top_p=0.95,
        )
        payload = response.choices[0].message.content
    except Exception as exc:  # pragma: no cover - external service
        # Fallback for potential custom client or older wrapper if it exists in environment
        try:
            response = client.responses.create(
                model=settings.openai_model,
                input=_build_prompt(request),
                temperature=0.7,
                max_output_tokens=2400,
                top_p=0.95,
            )
            payload = _extract_text(response)
        except:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    if not payload:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail="OpenAI returned an empty response")

    title, episode_text, guide_script, student_script = _parse_story_payload(payload, request.theme)
    episode_id = create_episode_id(title)
    episode_dir = ensure_episode_dir(episode_id)

    story = StoryResponse(
        episode_id=episode_id,
        title=title,
        episode_text=episode_text,
        guide_script=guide_script,
        student_script=student_script,
        dialogue=_build_dialogue(guide_script, student_script),
        word_count=_count_words(episode_text),
        language=request.language,
        model=settings.openai_model,
        episode_dir=str(episode_dir),
        guidance_audio={
            Voice.guide: "pending",
            Voice.student: "pending",
        },
    )
    return persist_story(story, db)
