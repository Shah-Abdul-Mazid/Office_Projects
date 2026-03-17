import hashlib
import json

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.audio import AudioAsset
from app.models.enums import AudioAssetType, ScriptStatus, SpeakerRole
from app.models.script import StoryScript
from app.services.contracts import RenderedAudioPayload
from app.services.storage_service import S3StorageService


class ElevenLabsTTSClient:
    def __init__(self, settings: Settings | None = None, http_client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings or get_settings()
        self.http_client = http_client or httpx.AsyncClient(
            base_url=self.settings.elevenlabs_base_url,
            timeout=60.0,
            headers={
                "xi-api-key": (
                    self.settings.elevenlabs_api_key.get_secret_value()
                    if self.settings.elevenlabs_api_key
                    else ""
                )
            },
        )

    async def render(self, *, text: str, voice_id: str) -> bytes:
        response = await self.http_client.post(
            f"/text-to-speech/{voice_id}",
            json={
                "text": text,
                "model_id": self.settings.elevenlabs_model_id,
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.7},
            },
        )
        response.raise_for_status()
        return response.content


class TTSPipelineService:
    def __init__(
        self,
        session: AsyncSession,
        settings: Settings | None = None,
        tts_client: ElevenLabsTTSClient | None = None,
        storage_service: S3StorageService | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.tts_client = tts_client or ElevenLabsTTSClient(self.settings)
        self.storage_service = storage_service or S3StorageService(self.settings)

    async def render_script_audio(self, script: StoryScript) -> list[AudioAsset]:
        assets: list[AudioAsset] = []
        for segment in sorted(script.segments, key=lambda item: item.sequence_index):
            voice_id = self._resolve_voice_id(script.voice_map, segment.speaker, segment.voice_id_override)
            audio_bytes = await self.tts_client.render(text=segment.content, voice_id=voice_id)
            checksum = hashlib.sha256(audio_bytes).hexdigest()
            object_key = f"scripts/{script.id}/segments/{segment.sequence_index:04d}.mp3"
            stored = await self.storage_service.upload_bytes(
                object_key=object_key,
                payload=audio_bytes,
                content_type="audio/mpeg",
                metadata={
                    "script_id": str(script.id),
                    "segment_id": str(segment.id),
                    "speaker": segment.speaker,
                },
            )
            rendered = RenderedAudioPayload(
                voice_id=voice_id,
                mime_type="audio/mpeg",
                size_bytes=len(audio_bytes),
                checksum_sha256=checksum,
                storage=stored,
            )
            asset = AudioAsset(
                script_id=script.id,
                segment_id=segment.id,
                asset_type=AudioAssetType.SEGMENT,
                provider="elevenlabs",
                voice_id=rendered.voice_id,
                mime_type=rendered.mime_type,
                size_bytes=rendered.size_bytes,
                checksum_sha256=rendered.checksum_sha256,
                storage_bucket=rendered.storage.bucket,
                storage_key=rendered.storage.key,
                public_url=rendered.storage.public_url,
                asset_metadata={
                    "speaker": segment.speaker,
                    "sequence_index": segment.sequence_index,
                },
            )
            self.session.add(asset)
            assets.append(asset)

        manifest = {
            "script_id": str(script.id),
            "segments": [
                {
                    "sequence_index": segment.sequence_index,
                    "speaker": segment.speaker,
                    "storage_key": f"scripts/{script.id}/segments/{segment.sequence_index:04d}.mp3",
                }
                for segment in sorted(script.segments, key=lambda item: item.sequence_index)
            ],
        }
        manifest_bytes = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
        manifest_object = await self.storage_service.upload_bytes(
            object_key=f"scripts/{script.id}/manifest.json",
            payload=manifest_bytes,
            content_type="application/json",
            metadata={"script_id": str(script.id)},
        )
        self.session.add(
            AudioAsset(
                script_id=script.id,
                asset_type=AudioAssetType.MANIFEST,
                provider="system",
                voice_id=None,
                mime_type="application/json",
                size_bytes=len(manifest_bytes),
                checksum_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                storage_bucket=manifest_object.bucket,
                storage_key=manifest_object.key,
                public_url=manifest_object.public_url,
                asset_metadata={"kind": "segment_manifest"},
            )
        )
        script.status = ScriptStatus.READY
        await self.session.flush()
        return assets

    def _resolve_voice_id(
        self,
        voice_map: dict,
        speaker: SpeakerRole,
        override_voice_id: str | None,
    ) -> str:
        if override_voice_id:
            return override_voice_id
        if speaker == SpeakerRole.GUIDE:
            return voice_map.get("guide_voice_id") or self.settings.guide_default_voice_id
        return voice_map.get("student_voice_id") or self.settings.student_default_voice_id
