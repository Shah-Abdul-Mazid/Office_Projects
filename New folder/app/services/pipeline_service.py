from uuid import UUID

from celery import chain

from app.workers.tasks.scripts import generate_script_task, render_script_audio_task


class PipelineDispatcher:
    @staticmethod
    def enqueue_story_pipeline(script_id: UUID, generation_job_id: UUID) -> None:
        chain(
            generate_script_task.s(str(script_id), str(generation_job_id)),
            render_script_audio_task.s(),
        ).apply_async()
