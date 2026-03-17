import asyncio
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionFactory
from app.models.enums import JobType, ProcessingStatus, ScriptStatus
from app.models.job import PipelineJob
from app.models.script import ScriptSegment, StoryScript
from app.schemas.script import ScriptGenerationRequest
from app.services.generation_service import ScriptGenerationService
from app.services.tts_service import TTSPipelineService
from app.workers.celery_app import celery_app


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def generate_script_task(self, script_id: str, job_id: str) -> dict[str, str]:
    return asyncio.run(_generate_script(script_id, job_id, self.request.id))


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def render_script_audio_task(self, pipeline_context: dict[str, str]) -> dict[str, str]:
    return asyncio.run(_render_script_audio(pipeline_context["script_id"], self.request.id))


async def _generate_script(script_id: str, job_id: str, task_id: str | None) -> dict[str, str]:
    script_uuid = UUID(script_id)
    job_uuid = UUID(job_id)
    async with AsyncSessionFactory() as session:
        statement = (
            select(StoryScript)
            .where(StoryScript.id == script_uuid)
            .options(selectinload(StoryScript.segments))
        )
        script = await session.scalar(statement)
        job = await session.get(PipelineJob, job_uuid)
        if script is None or job is None:
            raise RuntimeError("Pipeline resources not found")

        job.status = ProcessingStatus.RUNNING
        job.celery_task_id = task_id
        job.started_at = utcnow()
        job.attempt_count += 1
        script.status = ScriptStatus.GENERATING
        await session.commit()

        try:
            request_payload = ScriptGenerationRequest.model_validate(job.input_payload or {})
            generator = ScriptGenerationService()
            generated = await generator.generate_script(request_payload)

            for existing in list(script.segments):
                await session.delete(existing)
            await session.flush()

            compiled_lines: list[str] = []
            for segment_payload in generated.segments:
                compiled_lines.append(f"{segment_payload.speaker}: {segment_payload.content}")
                session.add(
                    ScriptSegment(
                        script_id=script.id,
                        sequence_index=segment_payload.sequence_index,
                        speaker=segment_payload.speaker,
                        content=segment_payload.content,
                        word_count=segment_payload.word_count,
                        segment_metadata={},
                    )
                )

            script.title = generated.title or script.title
            script.summary = generated.summary
            script.actual_word_count = generated.total_word_count
            script.script_text = "\n\n".join(compiled_lines)
            script.structured_payload = generated.model_dump(mode="json")
            script.model_name = generator.settings.openai_generation_model
            script.status = ScriptStatus.TTS_PENDING
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = utcnow()
            job.output_payload = {
                "segment_count": len(generated.segments),
                "total_word_count": generated.total_word_count,
            }
            await session.commit()
            return {"script_id": script_id}
        except Exception as exc:
            await session.rollback()
            await _mark_generation_failure(script_uuid, job_uuid, str(exc))
            raise


async def _render_script_audio(script_id: str, task_id: str | None) -> dict[str, str]:
    script_uuid = UUID(script_id)
    async with AsyncSessionFactory() as session:
        statement = (
            select(StoryScript)
            .where(StoryScript.id == script_uuid)
            .options(selectinload(StoryScript.segments))
        )
        script = await session.scalar(statement)
        if script is None:
            raise RuntimeError("Script not found for TTS processing")

        tts_job = PipelineJob(
            script_id=script.id,
            job_type=JobType.TTS_RENDER,
            status=ProcessingStatus.RUNNING,
            provider="elevenlabs",
            celery_task_id=task_id,
            attempt_count=1,
            input_payload={"segment_count": len(script.segments)},
            started_at=utcnow(),
        )
        session.add(tts_job)
        script.status = ScriptStatus.TTS_PROCESSING
        await session.commit()
        tts_job_id = tts_job.id

        try:
            assets = await TTSPipelineService(session).render_script_audio(script)
            tts_job.status = ProcessingStatus.COMPLETED
            tts_job.completed_at = utcnow()
            tts_job.output_payload = {"segment_asset_count": len(assets)}
            script.status = ScriptStatus.READY
            await session.commit()
            return {"script_id": script_id, "asset_count": str(len(assets))}
        except Exception as exc:
            await session.rollback()
            await _mark_tts_failure(script_uuid, tts_job_id, str(exc))
            raise


async def _mark_generation_failure(script_id: UUID, job_id: UUID, error_message: str) -> None:
    async with AsyncSessionFactory() as session:
        script = await session.get(StoryScript, script_id)
        job = await session.get(PipelineJob, job_id)
        if script is not None:
            script.status = ScriptStatus.FAILED
            script.error_message = error_message
        if job is not None:
            job.status = ProcessingStatus.FAILED
            job.error_message = error_message
            job.completed_at = utcnow()
        await session.commit()


async def _mark_tts_failure(script_id: UUID, job_id: UUID, error_message: str) -> None:
    async with AsyncSessionFactory() as session:
        script = await session.get(StoryScript, script_id)
        job = await session.get(PipelineJob, job_id)
        if script is not None:
            script.status = ScriptStatus.FAILED
            script.error_message = error_message
        if job is not None:
            job.status = ProcessingStatus.FAILED
            job.error_message = error_message
            job.completed_at = utcnow()
        await session.commit()
