from datetime import datetime, timezone
from uuid import uuid4

from app.config import settings
from app.moderation import moderate_content
from app.prompts import meditation_prompt, story_prompt
from app.providers import mock_provider, openai_provider
from app.schemas import GenerateRequest
from app.tts import synthesize_audio


def _provider():
    return mock_provider if settings.use_mock_ai else openai_provider


async def generate_content(item: GenerateRequest) -> dict:
    prompt = (
        meditation_prompt(item.title, item.growth_area, item.life_phase, item.minutes or 7)
        if item.type == 'meditation'
        else story_prompt(item.title, item.growth_area, item.life_phase, settings.min_words, settings.max_words)
    )

    generated = await _provider().generate_json_from_prompt(prompt)
    moderation = moderate_content(generated.get('content', ''))
    item_id = str(uuid4())[:12]
    tts = await synthesize_audio(generated.get('content', ''), item.voice, item_id)

    return {
        **generated,
        'moderation': moderation,
        'tts': tts,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
