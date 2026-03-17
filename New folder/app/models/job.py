from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import JobType, ProcessingStatus
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PipelineJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "pipeline_jobs"
    __table_args__ = (
        sa.Index("ix_pipeline_jobs_script_status", "script_id", "status"),
    )

    script_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        sa.ForeignKey("story_scripts.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_type: Mapped[JobType] = mapped_column(
        sa.Enum(JobType, name="job_type"),
        nullable=False,
    )
    status: Mapped[ProcessingStatus] = mapped_column(
        sa.Enum(ProcessingStatus, name="processing_status"),
        nullable=False,
        default=ProcessingStatus.QUEUED,
        server_default=sa.text("'queued'"),
    )
    provider: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(sa.String(255), nullable=True, unique=True)
    attempt_count: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
        server_default=sa.text("0"),
    )
    input_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    started_at: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    completed_at: Mapped[sa.DateTime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    script: Mapped[StoryScript] = relationship(back_populates="jobs")


from app.models.script import StoryScript  # noqa: E402
