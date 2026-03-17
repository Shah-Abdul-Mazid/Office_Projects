from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AudioAssetType, ProcessingStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AudioAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "audio_assets"
    __table_args__ = (
        sa.UniqueConstraint("storage_bucket", "storage_key", name="uq_audio_assets_storage_object"),
        sa.Index("ix_audio_assets_script_asset_type", "script_id", "asset_type"),
    )

    script_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("story_scripts.id", ondelete="CASCADE"),
        nullable=False,
    )
    segment_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("script_segments.id", ondelete="SET NULL"),
        nullable=True,
    )
    asset_type: Mapped[AudioAssetType] = mapped_column(
        sa.Enum(AudioAssetType, name="audio_asset_type"),
        nullable=False,
    )
    status: Mapped[ProcessingStatus] = mapped_column(
        sa.Enum(ProcessingStatus, name="audio_asset_status"),
        nullable=False,
        default=ProcessingStatus.COMPLETED,
        server_default=sa.text("'completed'"),
    )
    provider: Mapped[str] = mapped_column(sa.String(50), nullable=False, default="elevenlabs")
    voice_id: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    mime_type: Mapped[str] = mapped_column(sa.String(100), nullable=False, default="audio/mpeg")
    duration_ms: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(sa.BigInteger, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(sa.String(64), nullable=True)
    storage_bucket: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(sa.String(1024), nullable=False)
    public_url: Mapped[str | None] = mapped_column(sa.String(2048), nullable=True)
    asset_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb"),
    )

    script: Mapped[StoryScript] = relationship(back_populates="audio_assets")
    segment: Mapped[ScriptSegment | None] = relationship(back_populates="audio_assets")


from app.models.script import ScriptSegment, StoryScript  # noqa: E402
