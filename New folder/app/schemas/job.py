from datetime import datetime

from app.models.enums import JobType, ProcessingStatus
from app.schemas.common import TimestampedReadModel


class PipelineJobRead(TimestampedReadModel):
    job_type: JobType
    status: ProcessingStatus
    provider: str | None = None
    celery_task_id: str | None = None
    attempt_count: int
    input_payload: dict | None = None
    output_payload: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
