"""Content-addressable S3/MinIO storage client."""
from __future__ import annotations

import hashlib

import boto3
from botocore.config import Config as BotoConfig


class StorageClient:
    """Thin wrapper around boto3 S3 for content-addressable blob storage."""

    def __init__(
        self,
        bucket: str = "oem-manuals",
        endpoint_url: str | None = None,
        region: str = "us-east-1",
    ) -> None:
        self.bucket = bucket
        kwargs: dict = dict(region_name=region, config=BotoConfig(retries={"max_attempts": 5}))
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self._s3 = boto3.client("s3", **kwargs)

    # ------------------------------------------------------------------
    # Blob operations
    # ------------------------------------------------------------------

    def blob_key(self, sha256: str) -> str:
        return f"blobs/sha256/{sha256[:2]}/{sha256}"

    def ref_key(self, make: str, model: str, year: int, lang: str, revision: int) -> str:
        return f"refs/{make}/{model}/{year}/{lang}/{revision}.json"

    def put_blob(self, data: bytes, sha256: str | None = None) -> str:
        """Store blob; return sha256 hex digest."""
        if sha256 is None:
            sha256 = hashlib.sha256(data).hexdigest()
        key = self.blob_key(sha256)
        if not self._object_exists(key):
            self._s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ServerSideEncryption="aws:kms" if self._is_aws() else "AES256",
            )
        return sha256

    def get_blob(self, sha256: str) -> bytes:
        key = self.blob_key(sha256)
        resp = self._s3.get_object(Bucket=self.bucket, Key=key)
        return resp["Body"].read()

    def presigned_url(self, sha256: str, expiry: int = 3600) -> str:
        key = self.blob_key(sha256)
        return self._s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiry,
        )

    def put_ref(self, key: str, payload: bytes) -> None:
        self._s3.put_object(Bucket=self.bucket, Key=key, Body=payload)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _object_exists(self, key: str) -> bool:
        try:
            self._s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except self._s3.exceptions.ClientError:
            return False
        except Exception:
            return False

    def _is_aws(self) -> bool:
        ep = self._s3.meta.endpoint_url or ""
        if ep == "":
            return True
        from urllib.parse import urlparse
        parsed = urlparse(ep)
        hostname = parsed.hostname or ""
        return hostname == "amazonaws.com" or hostname.endswith(".amazonaws.com")
