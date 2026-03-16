import json
import re
import httpx
from app.config import settings


async def generate_json_from_prompt(prompt: str) -> dict:
    if not settings.openai_api_key:
        raise ValueError('OPENAI_API_KEY is required when USE_MOCK_AI=false')

    payload = {
        'model': settings.ai_model,
        'temperature': 0.7,
        'messages': [
            {'role': 'system', 'content': 'Return valid JSON only.'},
            {'role': 'user', 'content': prompt},
        ],
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {settings.openai_api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
        )

    if res.status_code >= 400:
        raise RuntimeError(f'OpenAI request failed: {res.status_code} {res.text}')

    text = res.json().get('choices', [{}])[0].get('message', {}).get('content', '{}')

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.S)
        if not match:
            raise ValueError('Model response was not valid JSON')
        return json.loads(match.group(0))
