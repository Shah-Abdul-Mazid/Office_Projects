from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ScriptStatus, SpeakerRole
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class StoryScript(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "story_scripts"
    __table_args__ = (
        sa.Index("ix_story_scripts_status_created_at", "status", "created_at"),
    )

    title: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    source_prompt: Mapped[str] = mapped_column(sa.Text, nullable=False)
    meditation_goal: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    audience: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    style_notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    language_code: Mapped[str] = mapped_column(
        sa.String(12),
        nullable=False,
        default="en-US",
        server_default=sa.text("'en-US'"),
    )
    target_word_count: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1200)
    actual_word_count: Mapped[int | None] = mapped_column(sa.Integer, nullable=True)
    status: Mapped[ScriptStatus] = mapped_column(
        sa.Enum(ScriptStatus, name="script_status"),
        nullable=False,
        default=ScriptStatus.QUEUED,
        server_default=sa.text("'queued'"),
        index=True,
    )
    provider: Mapped[str] = mapped_column(sa.String(50), nullable=False, default="openai")
    model_name: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    summary: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    script_text: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    structured_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    voice_map: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb"),
    )
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    segments: Mapped[list[ScriptSegment]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
        order_by="ScriptSegment.sequence_index",
        lazy="selectin",
    )
    audio_assets: Mapped[list[AudioAsset]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    jobs: Mapped[list[PipelineJob]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ScriptSegment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "script_segments"
    __table_args__ = (
        sa.UniqueConstraint("script_id", "sequence_index", name="uq_script_segments_script_sequence"),
        sa.Index("ix_script_segments_script_speaker", "script_id", "speaker"),
    )

    script_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("story_scripts.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence_index: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    speaker: Mapped[SpeakerRole] = mapped_column(
        sa.Enum(SpeakerRole, name="speaker_role"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(sa.Text, nullable=False)
    word_count: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    voice_id_override: Mapped[str | None] = mapped_column(sa.String(120), nullable=True)
    segment_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=sa.text("'{}'::jsonb"),
    )

    script: Mapped[StoryScript] = relationship(back_populates="segments")
    audio_assets: Mapped[list[AudioAsset]] = relationship(back_populates="segment", lazy="selectin")


from app.models.audio import AudioAsset  # noqa: E402
from app.models.job import PipelineJob  # noqa: E402
