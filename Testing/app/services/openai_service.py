import asyncio
from typing import Literal

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI, OpenAI, RateLimitError
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.exceptions import ExternalServiceTimeoutError, StorytellingServiceError

settings = get_settings()


class DialogueLine(BaseModel):
    role: Literal["Guide", "Student"]
    text: str = Field(min_length=10)


class DualRoleScript(BaseModel):
    dialogue: list[DialogueLine] = Field(min_length=12)


def _build_openai_messages(topic: str, language: str, retry_note: str | None = None) -> list[dict[str, str]]:
    system_prompt = (
        "You write immersive storytelling podcast scripts as a dialogue between two speakers. "
        "Return only structured output. The Guide is calm, wise, slow-paced, and uses grounded imagery. "
        "The Student is curious, questioning, reflective, and probes for meaning. "
        "Create a cohesive episode with a clear beginning, development, and resolution. "
        "Alternate speakers naturally and avoid stage directions, bullet points, or narrator labels beyond the role field. "
        "Keep the combined word count between 900 and 1500 words."
    )
    user_prompt = (
        f"Topic: {topic}\n"
        f"Language: {language}\n"
        "Write a complete episode script as a dialogue list. "
        "Make the conversation emotionally intelligent, educational, and suitable for spoken audio. "
        "Use concise but expressive turns so the final script works well with TTS."
    )
    if retry_note:
        user_prompt = f"{user_prompt}\n\nRevision requirement: {retry_note}"
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _word_count(script: DualRoleScript) -> int:
    return sum(len(line.text.split()) for line in script.dialogue)


async def generate_dual_role_script(topic: str, language: str) -> list[dict[str, str]]:
    client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds)
    retry_note: str | None = None

    for _ in range(2):
        try:
            response = await client.responses.parse(
                model=settings.openai_script_model,
                input=_build_openai_messages(topic=topic, language=language, retry_note=retry_note),
                text_format=DualRoleScript,
            )
        except APITimeoutError as exc:
            raise ExternalServiceTimeoutError("Script generation timed out while waiting for OpenAI.") from exc
        except (APIConnectionError, RateLimitError, APIError) as exc:
            raise StorytellingServiceError(f"Script generation failed: {exc}") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise StorytellingServiceError("OpenAI returned an empty structured script response.")

        word_count = _word_count(parsed)
        if 900 <= word_count <= 1500:
            return [line.model_dump() for line in parsed.dialogue]

        retry_note = (
            f"The last draft was {word_count} words. Regenerate the full script and keep the total between 900 and 1500 words."
        )

    raise StorytellingServiceError("OpenAI did not produce a script within the target word range after retrying.")


def _synthesize_speech_chunk_sync(text: str, voice: str, destination: str) -> None:
    client = OpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_seconds)
    with client.audio.speech.with_streaming_response.create(
        model=settings.openai_tts_model,
        voice=voice,
        input=text,
        response_format="mp3",
    ) as response:
        response.stream_to_file(destination)


async def synthesize_speech_chunk(text: str, voice: str, destination) -> None:
    try:
        await asyncio.to_thread(_synthesize_speech_chunk_sync, text, voice, str(destination))
    except APITimeoutError as exc:
        raise ExternalServiceTimeoutError("Audio generation timed out while waiting for OpenAI.") from exc
    except (APIConnectionError, RateLimitError, APIError) as exc:
        raise StorytellingServiceError(f"Audio generation failed: {exc}") from exc
