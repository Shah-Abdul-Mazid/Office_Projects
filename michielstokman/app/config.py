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
    min_story_words: int = field(default_factory=lambda: int(os.getenv("MIN_STORY_WORDS", "900")))
    max_story_words: int = field(default_factory=lambda: int(os.getenv("MAX_STORY_WORDS", "1500")))
    tts_output_dir: Path = field(default_factory=lambda: Path(os.getenv("TTS_OUTPUT_DIR", "output/audio")))
    voice_tld_overrides: Dict[str, str] = field(
        default_factory=lambda: {"guide": "com", "student": "co.uk"}
    )
    rss_feed_path: Path = field(default_factory=lambda: Path(os.getenv("RSS_FEED_PATH", "rss_feed.xml")))
    feedback_log_path: Path = field(default_factory=lambda: Path(os.getenv("FEEDBACK_LOG_PATH", "feedback_log.csv")))

settings = Settings()
settings.tts_output_dir.mkdir(parents=True, exist_ok=True)
