from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db_session
from app.models.enums import JobType, ProcessingStatus, ScriptStatus
from app.models.job import PipelineJob
from app.models.script import StoryScript
from app.schemas.audio import AudioAssetRead
from app.schemas.job import PipelineJobRead
from app.schemas.script import (
    GenerationAcceptedResponse,
    ScriptGenerationRequest,
    StoryScriptRead,
)
from app.services.pipeline_service import PipelineDispatcher

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.post("/generations", response_model=GenerationAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_script_generation(
    payload: ScriptGenerationRequest,
    session: AsyncSession = Depends(get_db_session),
) -> GenerationAcceptedResponse:
    script = StoryScript(
        title=payload.title_hint,
        source_prompt=payload.source_prompt,
        meditation_goal=payload.meditation_goal,
        audience=payload.audience,
        style_notes=payload.style_notes,
        language_code=payload.language_code,
        target_word_count=payload.target_word_count,
        status=ScriptStatus.QUEUED,
        provider="openai",
        model_name=None,
        voice_map=payload.voice_map.model_dump(),
    )
    job = PipelineJob(
        script=script,
        job_type=JobType.SCRIPT_GENERATION,
        status=ProcessingStatus.QUEUED,
        provider="openai",
        input_payload=payload.model_dump(mode="json"),
    )
    session.add_all([script, job])
    await session.commit()
    await session.refresh(script)
    await session.refresh(job)

    PipelineDispatcher.enqueue_story_pipeline(script.id, job.id)
    return GenerationAcceptedResponse(script_id=str(script.id), job_id=str(job.id), status=script.status)


@router.get("/{script_id}", response_model=StoryScriptRead)
async def get_script(script_id: UUID, session: AsyncSession = Depends(get_db_session)) -> StoryScriptRead:
    statement = (
        select(StoryScript)
        .where(StoryScript.id == script_id)
        .options(
            selectinload(StoryScript.segments),
            selectinload(StoryScript.audio_assets),
            selectinload(StoryScript.jobs),
        )
    )
    script = await session.scalar(statement)
    if script is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
    return StoryScriptRead.model_validate(script)


@router.get("/{script_id}/jobs", response_model=list[PipelineJobRead])
async def get_script_jobs(
    script_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> list[PipelineJobRead]:
    statement = (
        select(PipelineJob)
        .where(PipelineJob.script_id == script_id)
        .order_by(PipelineJob.created_at.asc())
    )
    jobs = (await session.scalars(statement)).all()
    return [PipelineJobRead.model_validate(job) for job in jobs]


@router.get("/{script_id}/audio", response_model=list[AudioAssetRead])
async def get_script_audio(
    script_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> list[AudioAssetRead]:
    statement = (
        select(StoryScript)
        .where(StoryScript.id == script_id)
        .options(selectinload(StoryScript.audio_assets))
    )
    script = await session.scalar(statement)
    if script is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Script not found")
    return [AudioAssetRead.model_validate(asset) for asset in script.audio_assets]
