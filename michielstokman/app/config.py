from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    edge_tts_voices: Dict[str, str] = field(
        default_factory=lambda: {
            "guide": os.getenv("EDGE_TTS_GUIDE_VOICE", "en-US-GuyNeural"),
            "student": os.getenv("EDGE_TTS_STUDENT_VOICE", "en-US-AvaNeural"),
        }
    )
    min_story_words: int = field(default_factory=lambda: int(os.getenv("MIN_STORY_WORDS", "900")))
    max_story_words: int = field(default_factory=lambda: int(os.getenv("MAX_STORY_WORDS", "1500")))
    tts_output_dir: Path = field(default_factory=lambda: Path(os.getenv("TTS_OUTPUT_DIR", "output/audio")))
    library_output_dir: Path = field(default_factory=lambda: Path(os.getenv("LIBRARY_OUTPUT_DIR", "output/library")))
    rss_feed_path: Path = field(default_factory=lambda: Path(os.getenv("RSS_FEED_PATH", "rss_feed.xml")))
    feedback_log_path: Path = field(default_factory=lambda: Path(os.getenv("FEEDBACK_LOG_PATH", "feedback_log.csv")))
    public_base_url: str = field(default_factory=lambda: os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./studio.db"))
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production-use-a-secure-key"))
    algorithm: str = field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")))
    
    # Meta Graph API
    meta_facebook_token: str = field(default_factory=lambda: os.getenv("META_FACEBOOK_TOKEN", ""))
    meta_instagram_token: str = field(default_factory=lambda: os.getenv("META_INSTAGRAM_TOKEN", ""))
    fb_page_id: str = field(default_factory=lambda: os.getenv("FB_PAGE_ID", ""))
    ig_user_id: str = field(default_factory=lambda: os.getenv("IG_USER_ID", ""))

    # Podcast & RSS Details
    podcast_author: str = field(default_factory=lambda: os.getenv("PODCAST_AUTHOR", "AI Meditation Studio"))
    podcast_category: str = field(default_factory=lambda: os.getenv("PODCAST_CATEGORY", "Health & Fitness > Mental Health"))
    podcast_explicit: str = field(default_factory=lambda: os.getenv("PODCAST_EXPLICIT", "no"))

settings = Settings()
settings.tts_output_dir.mkdir(parents=True, exist_ok=True)
settings.library_output_dir.mkdir(parents=True, exist_ok=True)
