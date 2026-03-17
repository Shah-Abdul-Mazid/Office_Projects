import json

from openai import AsyncOpenAI

from app.core.config import Settings, get_settings
from app.schemas.script import ScriptGenerationRequest
from app.services.contracts import GeneratedScriptPayload


class ScriptGenerationService:
    def __init__(self, settings: Settings | None = None, client: AsyncOpenAI | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client or AsyncOpenAI(
            api_key=(self.settings.openai_api_key.get_secret_value() if self.settings.openai_api_key else None),
            timeout=self.settings.openai_timeout_seconds,
        )

    def build_prompt(self, payload: ScriptGenerationRequest) -> str:
        schema = {
            "title": "optional string",
            "summary": "optional string",
            "total_word_count": payload.target_word_count,
            "segments": [
                {
                    "sequence_index": 1,
                    "speaker": "GUIDE or STUDENT",
                    "content": "segment text",
                    "word_count": 120,
                }
            ],
        }
        return (
            "Create a meditation storytelling script as strict JSON only. "
            f"Keep the final script between {self.settings.script_min_words} and "
            f"{self.settings.script_max_words} words. "
            "Use exactly two speakers named GUIDE and STUDENT. "
            f"Target approximately {payload.target_word_count} words. "
            f"Language: {payload.language_code}. "
            f"Story prompt: {payload.source_prompt}. "
            f"Meditation goal: {payload.meditation_goal or 'not specified'}. "
            f"Audience: {payload.audience or 'general'}. "
            f"Style notes: {payload.style_notes or 'calm, immersive, reflective'}. "
            "Return no markdown, prose, or explanations. "
            f"JSON schema example: {json.dumps(schema)}"
        )

    async def generate_script(self, payload: ScriptGenerationRequest) -> GeneratedScriptPayload:
        response = await self.client.responses.create(
            model=self.settings.openai_generation_model,
            input=[
                {
                    "role": "system",
                    "content": "You are a structured content engine for meditation storytelling.",
                },
                {"role": "user", "content": self.build_prompt(payload)},
            ],
        )
        parsed = GeneratedScriptPayload.model_validate_json(self._extract_json_payload(response))
        if not (self.settings.script_min_words <= parsed.total_word_count <= self.settings.script_max_words):
            raise ValueError("Generated script word count is outside the supported range")
        return parsed

    @staticmethod
    def _extract_json_payload(response: object) -> str:
        output_text = getattr(response, "output_text", None)
        if output_text:
            return output_text
        output_items = getattr(response, "output", None) or []
        for item in output_items:
            for content in getattr(item, "content", None) or []:
                text = getattr(content, "text", None)
                if text:
                    return text
        raise ValueError("OpenAI response did not contain parsable text output")
