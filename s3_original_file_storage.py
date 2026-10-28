"""Private S3-compatible object storage for original matter files.

The application must authorize the firm and case before calling this adapter.
The adapter uses opaque firm-scoped keys, conditional writes, server-side KMS
encryption, and no public URLs. Provider configuration and bucket policies
must be independently reviewed before production use.
"""
from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from typing import BinaryIO

from original_file_storage import ObjectStorageError, StagedObject

_OBJECT_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class S3PrivateObjectStore:
    """S3 API adapter; the client is injected to keep tests offline and deterministic."""

    client: object
    bucket: str
    kms_key_id: str
    max_bytes: int = 15_000_000

    def __post_init__(self):
        if not isinstance(self.bucket, str) or not self.bucket.strip():
            raise ValueError("a private object-storage bucket is required")
        if not isinstance(self.kms_key_id, str) or not self.kms_key_id.strip():
            raise ValueError("a managed KMS key identifier is required")
        if isinstance(self.max_bytes, bool) or not isinstance(self.max_bytes, int) or self.max_bytes < 1:
            raise ValueError("max_bytes must be a positive integer")

    @staticmethod
    def _firm_id(firm_id: int) -> int:
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("trusted firm_id must be a positive integer")
        return firm_id

    @staticmethod
    def _object_id(object_id: str) -> str:
        if not isinstance(object_id, str) or not _OBJECT_ID_RE.fullmatch(object_id):
            raise ValueError("invalid opaque object ID")
        return object_id

    def _key(self, firm_id: int, object_id: str, state: str) -> str:
        firm_id = self._firm_id(firm_id)
        object_id = self._object_id(object_id)
        if state not in {"staged", "blob"}:
            raise ValueError("invalid object state")
        return f"firms/{firm_id}/originals/{object_id}.{state}"

    @staticmethod
    def _missing(exc: Exception) -> bool:
        response = getattr(exc, "response", None)
        if not isinstance(response, dict):
            return False
        error = response.get("Error", {})
        metadata = response.get("ResponseMetadata", {})
        return error.get("Code") in {"404", "NoSuchKey", "NotFound"} or metadata.get("HTTPStatusCode") == 404

    def _head(self, key: str):
        try:
            return self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            if self._missing(exc):
                return None
            raise ObjectStorageError("object-storage metadata lookup failed") from exc

    def stage(self, firm_id: int, data: bytes) -> StagedObject:
        self._firm_id(firm_id)
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if len(data) > self.max_bytes:
            raise ObjectStorageError("object exceeds configured size limit")
        object_id = uuid.uuid4().hex
        key = self._key(firm_id, object_id, "staged")
        digest = hashlib.sha256(data).hexdigest()
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentLength=len(data),
                ContentType="application/octet-stream",
                Metadata={"sha256": digest, "firm-id": str(firm_id)},
                ServerSideEncryption="aws:kms",
                SSEKMSKeyId=self.kms_key_id,
                IfNoneMatch="*",
            )
        except Exception as exc:
            raise ObjectStorageError("could not stage original object") from exc
        return StagedObject(object_id, digest, len(data))

    def finalize(self, firm_id: int, object_id: str) -> None:
        staged = self._key(firm_id, object_id, "staged")
        final = self._key(firm_id, object_id, "blob")
        source = self._head(staged)
        if source is None:
            raise ObjectStorageError("staged object does not exist")
        if self._head(final) is not None:
            raise ObjectStorageError("final object already exists")
        etag = source.get("ETag")
        if not isinstance(etag, str) or not etag:
            raise ObjectStorageError("staged object has no usable version validator")
        try:
            self.client.copy_object(
                Bucket=self.bucket,
                Key=final,
                CopySource={"Bucket": self.bucket, "Key": staged},
                CopySourceIfMatch=etag,
                IfNoneMatch="*",
                MetadataDirective="COPY",
                ServerSideEncryption="aws:kms",
                SSEKMSKeyId=self.kms_key_id,
            )
            # If this delete fails, reconciliation can safely detect both keys.
            self.client.delete_object(Bucket=self.bucket, Key=staged)
        except Exception as exc:
            raise ObjectStorageError("could not finalize original object") from exc

    def open(self, firm_id: int, object_id: str) -> BinaryIO:
        key = self._key(firm_id, object_id, "blob")
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            body = response.get("Body")
            if body is None:
                raise ObjectStorageError("object-storage response has no body")
            return body
        except ObjectStorageError:
            raise
        except Exception as exc:
            raise ObjectStorageError("original object is unavailable") from exc

    def object_presence(self, firm_id: int, object_id: str) -> tuple[bool, bool]:
        staged = self._head(self._key(firm_id, object_id, "staged")) is not None
        final = self._head(self._key(firm_id, object_id, "blob")) is not None
        return staged, final

    def _verify(self, firm_id: int, object_id: str, state: str, *, expected_sha256: str, expected_size: int) -> bool:
        if not isinstance(expected_sha256, str) or not _SHA256_RE.fullmatch(expected_sha256):
            raise ValueError("expected_sha256 must be a lowercase SHA-256 digest")
        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
            raise ValueError("expected_size must be a non-negative integer")
        key = self._key(firm_id, object_id, state)
        digest = hashlib.sha256()
        size = 0
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            body = response.get("Body")
            if body is None:
                return False
            try:
                while True:
                    block = body.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    digest.update(block)
            finally:
                close = getattr(body, "close", None)
                if callable(close):
                    close()
        except Exception as exc:
            if self._missing(exc):
                return False
            raise ObjectStorageError("object integrity verification failed") from exc
        return size == expected_size and digest.hexdigest() == expected_sha256

    def verify(self, firm_id: int, object_id: str, *, expected_sha256: str, expected_size: int) -> bool:
        return self._verify(firm_id, object_id, "blob", expected_sha256=expected_sha256, expected_size=expected_size)

    def verify_staged(self, firm_id: int, object_id: str, *, expected_sha256: str, expected_size: int) -> bool:
        return self._verify(firm_id, object_id, "staged", expected_sha256=expected_sha256, expected_size=expected_size)

    def delete(self, firm_id: int, object_id: str) -> bool:
        keys = [self._key(firm_id, object_id, state) for state in ("staged", "blob")]
        existed = any(self._head(key) is not None for key in keys)
        try:
            for key in keys:
                self.client.delete_object(Bucket=self.bucket, Key=key)
            return existed
        except Exception as exc:
            raise ObjectStorageError("could not delete original object") from exc
