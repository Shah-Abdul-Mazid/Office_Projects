from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.episode import Episode, EpisodeStatus
from app.schemas.episode import EpisodeGenerateRequest, EpisodeRead
from app.services.audio_pipeline import run_audio_pipeline_task
from app.services.exceptions import ExternalServiceTimeoutError, StorytellingServiceError
from app.services.openai_service import generate_dual_role_script

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.post("/generate", response_model=EpisodeRead, status_code=status.HTTP_202_ACCEPTED)
async def generate_episode(
    payload: EpisodeGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Episode:
    episode = Episode(
        topic=payload.topic,
        language=payload.language,
        status=EpisodeStatus.PROCESSING,
    )
    db.add(episode)
    db.commit()
    db.refresh(episode)

    try:
        script = await generate_dual_role_script(payload.topic, payload.language)
        episode.script_json = script
        db.add(episode)
        db.commit()
        db.refresh(episode)
    except ExternalServiceTimeoutError as exc:
        episode.status = EpisodeStatus.FAILED
        episode.error_message = str(exc)
        db.add(episode)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        ) from exc
    except StorytellingServiceError as exc:
        episode.status = EpisodeStatus.FAILED
        episode.error_message = str(exc)
        db.add(episode)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    background_tasks.add_task(run_audio_pipeline_task, episode.id, script)
    return episode


@router.get("/{episode_id}", response_model=EpisodeRead)
def get_episode(episode_id: UUID, db: Session = Depends(get_db)) -> Episode:
    episode = db.get(Episode, episode_id)
    if episode is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode {episode_id} was not found.",
        )
    return episode
