from app.models.enums import AudioAssetType, ProcessingStatus
from app.schemas.common import TimestampedReadModel


class AudioAssetRead(TimestampedReadModel):
    asset_type: AudioAssetType
    status: ProcessingStatus
    provider: str
    voice_id: str | None = None
    mime_type: str
    duration_ms: int | None = None
    size_bytes: int | None = None
    checksum_sha256: str | None = None
    storage_bucket: str
    storage_key: str
    public_url: str | None = None
    asset_metadata: dict
