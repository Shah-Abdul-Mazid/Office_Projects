import httpx

from app.core.config import get_settings
from app.models.episode import Episode
from app.services.exceptions import ExternalServiceTimeoutError, StorytellingServiceError

settings = get_settings()


async def send_episode_webhook(episode: Episode) -> None:
    if not settings.webhook_url:
        return

    payload = {
        "episode_id": str(episode.id),
        "topic": episode.topic,
        "language": episode.language,
        "status": episode.status.value,
        "audio_url": episode.audio_url,
    }
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(str(settings.webhook_url), json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise ExternalServiceTimeoutError("Webhook notification timed out.") from exc
    except httpx.HTTPError as exc:
        raise StorytellingServiceError(f"Webhook notification failed: {exc}") from exc
