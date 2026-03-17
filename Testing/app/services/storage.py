import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin
from uuid import UUID

import boto3

from app.core.config import get_settings
from app.services.exceptions import StorytellingServiceError

settings = get_settings()


@dataclass(slots=True)
class StoredFile:
    storage_key: str
    url: str
    size_bytes: int


class StorageService:
    def __init__(self) -> None:
        self.settings = settings

    def store_episode_audio(self, source_path: Path, episode_id: UUID) -> StoredFile:
        filename = f"{episode_id}.mp3"
        if self.settings.audio_storage_mode == "s3":
            return self._store_s3(source_path=source_path, filename=filename)
        return self._store_local(source_path=source_path, filename=filename)

    def _store_local(self, source_path: Path, filename: str) -> StoredFile:
        destination = self.settings.local_audio_base_path / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        size_bytes = destination.stat().st_size

        relative_url = f"/media/audio/{filename}"
        url = (
            urljoin(f"{str(self.settings.public_base_url).rstrip('/')}/", f"media/audio/{filename}")
            if self.settings.public_base_url
            else relative_url
        )
        return StoredFile(storage_key=filename, url=url, size_bytes=size_bytes)

    def _store_s3(self, source_path: Path, filename: str) -> StoredFile:
        if not all(
            [
                self.settings.s3_bucket_name,
                self.settings.s3_access_key_id,
                self.settings.s3_secret_access_key,
                self.settings.s3_endpoint_url,
            ]
        ):
            raise StorytellingServiceError("S3 storage is enabled but the required S3 settings are incomplete.")

        object_key = f"episodes/{filename}"
        client = boto3.client(
            "s3",
            endpoint_url=str(self.settings.s3_endpoint_url),
            aws_access_key_id=self.settings.s3_access_key_id,
            aws_secret_access_key=self.settings.s3_secret_access_key,
            region_name=self.settings.s3_region_name,
        )
        client.upload_file(
            str(source_path),
            self.settings.s3_bucket_name,
            object_key,
            ExtraArgs={"ContentType": "audio/mpeg"},
        )

        size_bytes = source_path.stat().st_size
        if self.settings.s3_public_base_url:
            url = urljoin(f"{str(self.settings.s3_public_base_url).rstrip('/')}/", object_key)
        else:
            url = (
                f"{str(self.settings.s3_endpoint_url).rstrip('/')}/"
                f"{self.settings.s3_bucket_name}/{object_key}"
            )
        return StoredFile(storage_key=object_key, url=url, size_bytes=size_bytes)


def get_storage_service() -> StorageService:
    return StorageService()
