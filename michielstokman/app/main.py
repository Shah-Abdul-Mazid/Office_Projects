from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
import os

from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from app.config import settings
from app.database import engine, Base, get_db, SessionLocal
from app.models import User, Episode
from app.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_active_user,
    get_password_hash,
    verify_password
)
from app.schemas import (
    BulkStoryResponse,
    EpisodeSummary,
    FeedbackRequest,
    FeedbackResponse,
    OrchestrationResponse,
    StoryBatchRequest,
    StoryRequest,
    StoryResponse,
    TTSRequest,
    TTSResponse,
    Voice,
    Token
)
from app.services.ai_story import generate_episode
from app.services.library import get_episode_dir, list_episode_summaries, load_story
from app.services.orchestrator import append_feedback, attach_role_audio, orchestrate_story
from app.services.tts import TTSResult, synthesize_voice
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Story & Meditation Studio",
    version="0.2.0",
    description="Generate long-form meditation episodes, split Guide/Student voice tracks, and manage publishing assets with FastAPI.",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        # Create default admin if it doesn't exist
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin123")
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            hashed_pw = get_password_hash(admin_pass)
            new_admin = User(email=admin_email, hashed_password=hashed_pw, is_admin=True)
            db.add(new_admin)
            db.commit()
            print(f"Created default admin: {admin_email}")
    finally:
        db.close()


@lru_cache()
def get_openai_client() -> OpenAI:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="OPENAI_API_KEY must be configured before requesting content.",
        )
    return OpenAI(api_key=settings.openai_api_key)


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/episodes", response_model=list[EpisodeSummary])
async def list_episodes(db: Session = Depends(get_db)) -> list[EpisodeSummary]:
    return list_episode_summaries(db)


@app.get("/episodes/{episode_id}", response_model=StoryResponse)
async def get_episode(episode_id: str, db: Session = Depends(get_db)) -> StoryResponse:
    return load_story(episode_id, db)


@app.post("/episodes/{episode_id}/voiceover", response_model=StoryResponse)
async def create_voiceover_for_episode(
    episode_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StoryResponse:
    story = load_story(episode_id, db)
    return await attach_role_audio(story, db)


@app.post("/stories", response_model=StoryResponse)
async def create_episode(
    request: StoryRequest, 
    client: OpenAI = Depends(get_openai_client),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StoryResponse:
    return await generate_episode(request, client, db)


@app.post("/stories/full", response_model=StoryResponse)
async def create_episode_with_narration(
    request: StoryRequest, 
    client: OpenAI = Depends(get_openai_client),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StoryResponse:
    story = await generate_episode(request, client, db)
    return await attach_role_audio(story, db)


async def _process_bulk_batch(
    request: StoryBatchRequest, 
    client: OpenAI, 
    db_session_factory: Any,
):
    # This runs in the background
    db = db_session_factory()
    try:
        base_payload = request.model_dump(exclude={"count", "include_audio"})
        for batch_index in range(1, request.count + 1):
            story_payload = dict(base_payload)
            focus = story_payload.get("focus")
            if focus:
                story_payload["focus"] = f"{focus} (bulk {batch_index})"
            
            story_req = StoryRequest(**story_payload)
            if request.include_audio:
                await orchestrate_story(story_req, client, db)
            else:
                await generate_episode(story_req, client, db)
            
            print(f"BULK: Completed episode {batch_index}/{request.count}")
    finally:
        db.close()


@app.post("/stories/bulk", status_code=status.HTTP_202_ACCEPTED)
async def create_bulk_episodes(
    request: StoryBatchRequest, 
    background_tasks: BackgroundTasks,
    client: OpenAI = Depends(get_openai_client),
    current_user: User = Depends(get_current_active_user)
):
    """
    Triggers bulk generation for the content library.
    Returns immediately and processes in the background as requested in Phase 3.
    """
    background_tasks.add_task(_process_bulk_batch, request, client, SessionLocal)
    return {
        "status": "processing",
        "message": f"Bulk generation of {request.count} episodes started in background.",
        "estimated_completion": f"Approx {request.count * 2} minutes"
    }


@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_release(
    request: StoryRequest, 
    client: OpenAI = Depends(get_openai_client),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> OrchestrationResponse:
    payload = await orchestrate_story(request, client, db)
    return OrchestrationResponse(**payload)


@app.post("/stories/tts", response_model=TTSResponse)
async def narrate_story(
    payload: TTSRequest,
    current_user: User = Depends(get_current_active_user)
) -> TTSResponse:
    result: TTSResult = await synthesize_voice(
        payload.text,
        payload.voice,
        language=payload.language,
        episode_id=payload.episode_id,
        audio_format=payload.audio_format,
    )
    return TTSResponse(voice=result.voice, audio_path=str(result.path), episode_id=payload.episode_id)


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    append_feedback(payload, db)
    return FeedbackResponse(status="recorded")


@app.get("/episodes/{episode_id}/audio/{file_name}")
async def fetch_episode_audio(episode_id: str, file_name: str) -> FileResponse:
    episode_dir = get_episode_dir(episode_id).resolve()
    target_file = (episode_dir / Path(file_name).name).resolve()
    
    # Enhanced debugging for file access
    print(f"DEBUG: Audio request for {episode_id}/{file_name}")
    print(f"DEBUG: Resolved path: {target_file}")
    
    if not target_file.exists():
        print(f"DEBUG: File NOT FOUND at {target_file}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Requested audio file is missing"
        )
    
    return FileResponse(
        str(target_file), 
        media_type="audio/mpeg", 
        filename=target_file.name,
        headers={"Accept-Ranges": "bytes"}
    )


@app.get("/audio/{file_name}")
async def fetch_legacy_audio(file_name: str) -> FileResponse:
    # Check root tts output dir first
    target_file = settings.tts_output_dir / Path(file_name).name
    if target_file.exists():
        return FileResponse(target_file, media_type="audio/mpeg", filename=target_file.name)
    
    # Fallback: Search all episode directories in library
    if settings.library_output_dir.exists():
        for episode_dir in settings.library_output_dir.iterdir():
            if episode_dir.is_dir():
                potential = episode_dir / Path(file_name).name
                if potential.exists():
                    return FileResponse(
                        str(potential.resolve()), 
                        media_type="audio/mpeg", 
                        filename=potential.name,
                        headers={"Accept-Ranges": "bytes"}
                    )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Requested audio file is missing"
    )
