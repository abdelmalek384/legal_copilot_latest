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
from dataclasses import dataclass, field
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
    kms_client: object | None = None
    _accepted_kms_key_ids: frozenset[str] = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        if not isinstance(self.bucket, str) or not self.bucket.strip():
            raise ValueError("a private object-storage bucket is required")
        if not isinstance(self.kms_key_id, str) or not self.kms_key_id.strip():
            raise ValueError("a managed KMS key identifier is required")
        if isinstance(self.max_bytes, bool) or not isinstance(self.max_bytes, int) or self.max_bytes < 1:
            raise ValueError("max_bytes must be a positive integer")
        if self.kms_client is None:
            if self.kms_key_id.startswith("alias/"):
                raise ValueError("a KMS client is required to resolve KMS key aliases")
            accepted = {self.kms_key_id}
        else:
            try:
                metadata = self.kms_client.describe_key(KeyId=self.kms_key_id).get("KeyMetadata", {})
            except Exception as exc:
                raise ValueError("configured KMS key could not be resolved") from exc
            accepted = {
                value for value in (metadata.get("KeyId"), metadata.get("Arn"))
                if isinstance(value, str) and value.strip()
            }
            if not accepted:
                raise ValueError("configured KMS key did not resolve to a canonical identity")
        object.__setattr__(self, "_accepted_kms_key_ids", frozenset(accepted))

    def _is_expected_kms_key(self, response: dict) -> bool:
        key_id = response.get("SSEKMSKeyId")
        return (
            response.get("ServerSideEncryption") == "aws:kms"
            and isinstance(key_id, str)
            and key_id in self._accepted_kms_key_ids
        )

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
            result = self.client.head_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            if self._missing(exc):
                return None
            raise ObjectStorageError("object-storage metadata lookup failed") from exc
        # Do not treat an object as valid merely because its key exists. Require
        # S3's response to attest that server-side KMS encryption is active.
        if not self._is_expected_kms_key(result):
            raise ObjectStorageError("stored object is not protected by the configured KMS key")
        return result

    def stage(self, firm_id: int, data: bytes) -> StagedObject:
        """Stage bytes under a newly generated opaque object ID."""
        return self.stage_with_id(firm_id, uuid.uuid4().hex, data)

    def stage_with_id(self, firm_id: int, object_id: str, data: bytes) -> StagedObject:
        """Stage a verified restore object while preserving its immutable object ID."""
        firm_id = self._firm_id(firm_id)
        object_id = self._object_id(object_id)
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if len(data) > self.max_bytes:
            raise ObjectStorageError("object exceeds configured size limit")
        staged_key = self._key(firm_id, object_id, "staged")
        final_key = self._key(firm_id, object_id, "blob")
        if self._head(staged_key) is not None or self._head(final_key) is not None:
            raise ObjectStorageError("object ID already exists in target storage")
        digest = hashlib.sha256(data).hexdigest()
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=staged_key,
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
            # Never delete the recoverable staged copy until the destination is
            # independently observed and its encryption/key identity is verified.
            # Also verify the copied bytes against the digest/size recorded at stage
            # time: a successful copy API response is not an integrity guarantee.
            expected_digest = source.get("Metadata", {}).get("sha256")
            expected_size = source.get("ContentLength")
            if (
                not isinstance(expected_digest, str)
                or not _SHA256_RE.fullmatch(expected_digest)
                or isinstance(expected_size, bool)
                or not isinstance(expected_size, int)
                or expected_size < 0
            ):
                raise ObjectStorageError("staged object has invalid integrity metadata")
            destination = self._head(final)
            if destination is None:
                raise ObjectStorageError("finalized object is missing")
            if not self.verify(
                firm_id, object_id,
                expected_sha256=expected_digest,
                expected_size=expected_size,
            ):
                raise ObjectStorageError("finalized object failed integrity verification")
            self.client.delete_object(Bucket=self.bucket, Key=staged)
        except Exception as exc:
            raise ObjectStorageError("could not finalize original object") from exc

    def open(self, firm_id: int, object_id: str) -> BinaryIO:
        key = self._key(firm_id, object_id, "blob")
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            body = response.get("Body")
            if not self._is_expected_kms_key(response):
                close = getattr(body, "close", None)
                if callable(close):
                    close()
                raise ObjectStorageError("stored object is not protected by KMS encryption")
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
            # Match the exact configured KMS key identity here too. Do not
            # let the streaming integrity path accept any arbitrary KMS key
            # merely because the ciphertext is encrypted.
            if not self._is_expected_kms_key(response):
                close = getattr(body, "close", None)
                if callable(close):
                    close()
                return False
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

    def list_object_keys(self) -> set[str]:
        """List keys in the dedicated originals namespace; never returns object bytes."""
        prefix = "firms/"
        found: set[str] = set()
        token = None
        try:
            while True:
                args = {"Bucket": self.bucket, "Prefix": prefix}
                if token:
                    args["ContinuationToken"] = token
                response = self.client.list_objects_v2(**args)
                for item in response.get("Contents", []):
                    key = item.get("Key")
                    if isinstance(key, str):
                        found.add(key)
                if not response.get("IsTruncated"):
                    return found
                token = response.get("NextContinuationToken")
                if not token:
                    raise ObjectStorageError("object-storage listing omitted its continuation token")
        except ObjectStorageError:
            raise
        except Exception as exc:
            raise ObjectStorageError("object-storage inventory could not be listed") from exc

    def purge_unversioned(
        self, firm_id: int, object_id: str, *, expected_sha256: str, expected_size: int
    ) -> bool:
        """Physically remove one finalized object only from a never-versioned bucket.

        This deliberately refuses both Enabled and Suspended versioning. A suspended
        bucket may retain historical versions, and deleting the current key would only
        create/alter a delete marker rather than prove erasure. Production callers must
        additionally enforce the approved retention policy, target fingerprint,
        IAM controls, quiescence, and independent authorization.
        """
        firm_id = self._firm_id(firm_id)
        object_id = self._object_id(object_id)
        try:
            versioning = self.client.get_bucket_versioning(Bucket=self.bucket)
        except Exception as exc:
            raise ObjectStorageError("bucket versioning state could not be verified") from exc
        if not isinstance(versioning, dict):
            raise ObjectStorageError("physical purge requires a confirmed never-versioned bucket")
        status = versioning.get("Status")
        if status in ("Enabled", "Suspended"):
            raise ObjectStorageError("physical purge is blocked for a versioned or suspended bucket; a confirmed never-versioned bucket is required")
        unexpected_fields = set(versioning) - {"ResponseMetadata"}
        if status is not None or unexpected_fields:
            raise ObjectStorageError("physical purge requires a confirmed never-versioned bucket")
        staged_key = self._key(firm_id, object_id, "staged")
        final_key = self._key(firm_id, object_id, "blob")
        if self._head(staged_key) is not None:
            raise ObjectStorageError("physical purge is blocked while a staged copy exists")
        final_head = self._head(final_key)
        if final_head is None:
            return False
        etag = final_head.get("ETag")
        if not isinstance(etag, str) or not etag.strip():
            raise ObjectStorageError("physical purge requires an object ETag for conditional deletion")
        if not self.verify(
            firm_id, object_id,
            expected_sha256=expected_sha256, expected_size=expected_size,
        ):
            raise ObjectStorageError("original bytes failed integrity verification before purge")
        try:
            # Bind deletion to the exact object version observed before integrity
            # verification. S3 returns 412 if a concurrent writer changed the ETag.
            result = self.client.delete_object(
                Bucket=self.bucket, Key=final_key, IfMatch=etag
            )
            version_id = result.get("VersionId")
            if version_id not in (None, "null"):
                raise ObjectStorageError("delete created a versioned marker; physical purge is unproven")
            if self._head(final_key) is not None:
                raise ObjectStorageError("object remains after physical purge request")
            after = self.client.get_bucket_versioning(Bucket=self.bucket)
            if (
                not isinstance(after, dict)
                or after.get("Status") is not None
                or set(after) - {"ResponseMetadata"}
            ):
                raise ObjectStorageError("bucket versioning changed or became unknown during physical purge")
            return True
        except ObjectStorageError:
            raise
        except Exception as exc:
            raise ObjectStorageError("physical purge could not be verified") from exc

    def delete(self, firm_id: int, object_id: str) -> bool:
        keys = [self._key(firm_id, object_id, state) for state in ("staged", "blob")]
        existed = any(self._head(key) is not None for key in keys)
        try:
            for key in keys:
                self.client.delete_object(Bucket=self.bucket, Key=key)
            return existed
        except Exception as exc:
            raise ObjectStorageError("could not delete original object") from exc
