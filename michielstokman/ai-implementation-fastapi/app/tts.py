from app.config import settings


async def synthesize_audio(text: str, voice: str, item_id: str) -> dict:
    if not text:
        raise ValueError('Missing text for TTS')

    if not settings.elevenlabs_api_key:
        return {
            'status': 'mock_ready',
            'provider': 'mock',
            'voice': voice,
            'audio_url': f'https://audio.local/{item_id}-{voice}.mp3',
            'note': 'ELEVENLABS_API_KEY not set; returning mock URL',
        }

    return {
        'status': 'queued',
        'provider': 'elevenlabs',
        'voice': voice,
        'audio_url': None,
        'note': 'Implement ElevenLabs API call + storage upload in production',
    }
