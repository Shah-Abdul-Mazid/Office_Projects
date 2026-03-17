import asyncio

import boto3

from app.core.config import Settings, get_settings
from app.services.contracts import StoredObject


class S3StorageService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client = boto3.client(
            "s3",
            region_name=self.settings.s3_region,
            endpoint_url=self.settings.s3_endpoint_url,
            aws_access_key_id=(
                self.settings.aws_access_key_id.get_secret_value()
                if self.settings.aws_access_key_id
                else None
            ),
            aws_secret_access_key=(
                self.settings.aws_secret_access_key.get_secret_value()
                if self.settings.aws_secret_access_key
                else None
            ),
        )

    async def upload_bytes(
        self,
        *,
        object_key: str,
        payload: bytes,
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> StoredObject:
        return await asyncio.to_thread(
            self._upload_bytes_sync,
            object_key,
            payload,
            content_type,
            metadata or {},
        )

    def _upload_bytes_sync(
        self,
        object_key: str,
        payload: bytes,
        content_type: str,
        metadata: dict[str, str],
    ) -> StoredObject:
        self._client.put_object(
            Bucket=self.settings.s3_bucket,
            Key=object_key,
            Body=payload,
            ContentType=content_type,
            Metadata=metadata,
        )
        return StoredObject(
            bucket=self.settings.s3_bucket,
            key=object_key,
            public_url=self._build_public_url(object_key),
        )

    def _build_public_url(self, object_key: str) -> str:
        if self.settings.s3_endpoint_url:
            return f"{self.settings.s3_endpoint_url.rstrip('/')}/{self.settings.s3_bucket}/{object_key}"
        return f"https://{self.settings.s3_bucket}.s3.{self.settings.s3_region}.amazonaws.com/{object_key}"
