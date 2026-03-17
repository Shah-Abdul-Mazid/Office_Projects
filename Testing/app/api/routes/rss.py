from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.episode import Episode, EpisodeStatus
from app.services.rss import build_podcast_rss

router = APIRouter(prefix="/rss", tags=["rss"])


@router.get("/podcast.xml")
def get_podcast_feed(request: Request, db: Session = Depends(get_db)) -> Response:
    episodes = db.scalars(
        select(Episode)
        .where(Episode.status == EpisodeStatus.COMPLETED)
        .order_by(Episode.published_at.desc(), Episode.created_at.desc())
    ).all()
    xml_payload = build_podcast_rss(episodes=episodes, base_url=str(request.base_url))
    return Response(content=xml_payload, media_type="application/rss+xml")
