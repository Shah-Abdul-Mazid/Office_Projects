from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Storytelling Platform"
    environment: str = "development"
    api_v1_prefix: str = ""

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/storytelling"

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_script_model: str = "gpt-4o"
    openai_tts_model: str = "tts-1"
    request_timeout_seconds: float = 60.0
    tts_chunk_max_chars: int = 1300

    audio_storage_mode: Literal["local", "s3"] = "local"
    local_audio_base_path: Path = Path("storage/audio")
    local_chunk_base_path: Path = Path("storage/chunks")
    public_base_url: AnyHttpUrl | None = None

    s3_endpoint_url: AnyHttpUrl | None = None
    s3_bucket_name: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_region_name: str | None = None
    s3_public_base_url: AnyHttpUrl | None = None

    webhook_url: AnyHttpUrl | None = None

    podcast_title: str = "Guide and Student Stories"
    podcast_description: str = (
        "A reflective AI storytelling series featuring a wise Guide and a curious Student."
    )
    podcast_author: str = "AI Storytelling Platform"
    podcast_language: str = "en-us"
    podcast_category: str = "Education"
    podcast_explicit: str = "false"
    podcast_image_url: AnyHttpUrl | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def ensure_storage_dirs(self) -> None:
        self.local_audio_base_path.mkdir(parents=True, exist_ok=True)
        self.local_chunk_base_path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_storage_dirs()
    return settings
