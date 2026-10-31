"""Version-pinned transport for encrypted database recovery bundles in S3.

The bundle is already application-encrypted with BACKUP_KEY. This module adds
independent S3 SSE-KMS protection and refuses unversioned or ambiguous objects.
It never activates a restored database; callers pass the downloaded bundle to
restore_backup_bundle(), which requires a new isolated destination.
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
import uuid
from pathlib import Path
from typing import Any

from database_backup import DatabaseBundleError, _MAX_ENCRYPTED_BUNDLE_BYTES

_PREFIX = "database-recovery/v1/"
_PART_SIZE = 64 * 1024 * 1024
_MAX_PARTS = 10_000
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _fail(message: str) -> None:
    raise DatabaseBundleError(message)


def _digest_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            size += len(block)
            if size > _MAX_ENCRYPTED_BUNDLE_BYTES:
                _fail("Encrypted backup exceeds the supported size limit")
            digest.update(block)
    return digest.hexdigest(), size


def _require_versioning(s3_client: Any, bucket: str) -> None:
    if not isinstance(bucket, str) or not bucket.strip():
        _fail("Recovery archive bucket is required")
    try:
        state = s3_client.get_bucket_versioning(Bucket=bucket)
    except Exception as exc:
        raise DatabaseBundleError("Recovery archive versioning could not be verified") from exc
    if not isinstance(state, dict) or state.get("Status") != "Enabled":
        _fail("Recovery archive bucket versioning must be Enabled")


def _key_arn(kms_client: Any, key_id: str) -> str:
    if not isinstance(key_id, str) or not key_id.strip():
        _fail("Recovery archive KMS key ID is required")
    try:
        metadata = kms_client.describe_key(KeyId=key_id).get("KeyMetadata", {})
    except Exception as exc:
        raise DatabaseBundleError("Recovery archive KMS key could not be inspected") from exc
    arn = metadata.get("Arn")
    if (
        not isinstance(arn, str)
        or metadata.get("KeyState") != "Enabled"
        or metadata.get("KeyUsage") != "ENCRYPT_DECRYPT"
        or metadata.get("KeySpec") != "SYMMETRIC_DEFAULT"
        or metadata.get("KeyManager") != "CUSTOMER"
    ):
        _fail("Recovery archive requires an enabled customer-managed symmetric KMS key")
    return arn


def _safe_source(path_value: str | Path) -> Path:
    path = Path(path_value).expanduser()
    if path.is_symlink():
        _fail("Backup input must not be a symlink")
    try:
        info = path.stat(follow_symlinks=False)
    except OSError as exc:
        raise DatabaseBundleError("Backup input could not be inspected") from exc
    if not stat.S_ISREG(info.st_mode):
        _fail("Backup input must be a regular file")
    if info.st_size <= 0 or info.st_size > _MAX_ENCRYPTED_BUNDLE_BYTES:
        _fail("Encrypted backup size is outside the supported range")
    return path


def upload_encrypted_bundle(
    s3_client: Any,
    kms_client: Any,
    bundle_path: str | Path,
    *,
    bucket: str,
    kms_key_id: str,
) -> dict[str, Any]:
    """Upload an opaque encrypted bundle and return its exact S3 version locator."""
    source = _safe_source(bundle_path)
    _require_versioning(s3_client, bucket)
    key_arn = _key_arn(kms_client, kms_key_id)
    digest, size = _digest_file(source)
    object_key = _PREFIX + uuid.uuid4().hex + ".dbbundle.enc"
    metadata = {"sha256": digest, "format": "encrypted-database-bundle-v2"}
    response: dict[str, Any]
    if size <= 5 * 1024 * 1024 * 1024:
        try:
            with source.open("rb") as body:
                response = s3_client.put_object(
                    Bucket=bucket,
                    Key=object_key,
                    Body=body,
                    ContentLength=size,
                    ContentType="application/octet-stream",
                    Metadata=metadata,
                    ServerSideEncryption="aws:kms",
                    SSEKMSKeyId=key_arn,
                )
        except Exception as exc:
            raise DatabaseBundleError("Encrypted recovery bundle upload failed") from exc
    else:
        upload_id = None
        parts = []
        try:
            created = s3_client.create_multipart_upload(
                Bucket=bucket, Key=object_key,
                ContentType="application/octet-stream", Metadata=metadata,
                ServerSideEncryption="aws:kms", SSEKMSKeyId=key_arn,
            )
            upload_id = created.get("UploadId")
            if not isinstance(upload_id, str) or not upload_id:
                _fail("S3 did not return a multipart upload identifier")
            with source.open("rb") as body:
                part_number = 1
                while True:
                    chunk = body.read(_PART_SIZE)
                    if not chunk:
                        break
                    if part_number > _MAX_PARTS:
                        _fail("Encrypted recovery bundle exceeds the S3 multipart part limit")
                    uploaded = s3_client.upload_part(
                        Bucket=bucket, Key=object_key, UploadId=upload_id,
                        PartNumber=part_number, Body=chunk,
                    )
                    etag = uploaded.get("ETag")
                    if not isinstance(etag, str) or not etag:
                        _fail("S3 multipart upload returned a part without an ETag")
                    parts.append({"PartNumber": part_number, "ETag": etag})
                    part_number += 1
            response = s3_client.complete_multipart_upload(
                Bucket=bucket, Key=object_key, UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )
            upload_id = None
        except Exception as exc:
            if upload_id:
                try:
                    s3_client.abort_multipart_upload(
                        Bucket=bucket, Key=object_key, UploadId=upload_id
                    )
                except Exception:
                    pass
            if isinstance(exc, DatabaseBundleError):
                raise
            raise DatabaseBundleError("Encrypted recovery bundle multipart upload failed") from exc

    version_id = response.get("VersionId")
    if not isinstance(version_id, str) or not version_id or version_id == "null":
        _fail("S3 did not return an immutable archive version ID; upload is not accepted")
    try:
        accepted = s3_client.head_object(
            Bucket=bucket, Key=object_key, VersionId=version_id
        )
    except Exception as exc:
        raise DatabaseBundleError("Uploaded recovery archive version could not be verified") from exc
    if (
        accepted.get("VersionId") != version_id
        or accepted.get("ServerSideEncryption") != "aws:kms"
        or accepted.get("SSEKMSKeyId") != key_arn
        or accepted.get("ContentLength") != size
        or accepted.get("Metadata", {}).get("sha256") != digest
        or accepted.get("Metadata", {}).get("format") != "encrypted-database-bundle-v2"
    ):
        _fail("Uploaded recovery archive version failed exact-version KMS/metadata acceptance")
    # Verify the bytes that S3 actually persisted, not only caller-supplied metadata.
    probe = None
    try:
        probe = s3_client.get_object(
            Bucket=bucket, Key=object_key, VersionId=version_id
        )
        if probe.get("VersionId") != version_id or probe.get("Body") is None:
            _fail("S3 upload verification did not return the exact object version")
        persisted_digest = hashlib.sha256()
        persisted_size = 0
        body = probe["Body"]
        while True:
            block = body.read(1024 * 1024)
            if not block:
                break
            persisted_size += len(block)
            if persisted_size > size:
                _fail("Persisted archive version exceeds the uploaded size")
            persisted_digest.update(block)
        if persisted_size != size or persisted_digest.hexdigest() != digest:
            _fail("Persisted archive bytes do not match the uploaded bundle checksum")
    except DatabaseBundleError:
        raise
    except Exception as exc:
        raise DatabaseBundleError("Persisted recovery archive bytes could not be verified") from exc
    finally:
        if probe is not None and probe.get("Body") is not None:
            probe["Body"].close()
    return {
        "bucket": bucket,
        "key": object_key,
        "version_id": version_id,
        "sha256": digest,
        "size_bytes": size,
        "kms_key_arn": key_arn,
        "format": "encrypted-database-bundle-v2",
    }


def download_encrypted_bundle_version(
    s3_client: Any,
    kms_client: Any,
    locator: dict[str, Any],
    destination: str | Path,
    *,
    bucket: str,
    kms_key_id: str,
) -> Path:
    """Fetch one exact version, validate encryption/metadata/bytes, and write exclusively."""
    _require_versioning(s3_client, bucket)
    key_arn = _key_arn(kms_client, kms_key_id)
    if not isinstance(locator, dict):
        _fail("Recovery archive locator is malformed")
    key = locator.get("key")
    version_id = locator.get("version_id")
    expected_digest = locator.get("sha256")
    expected_size = locator.get("size_bytes")
    if (
        locator.get("bucket") != bucket
        or not isinstance(key, str) or not key.startswith(_PREFIX)
        or "/" in key[len(_PREFIX):]
        or not isinstance(version_id, str) or not version_id or version_id == "null"
        or not isinstance(expected_digest, str) or not _SHA256.fullmatch(expected_digest)
        or not isinstance(expected_size, int) or expected_size <= 0
        or expected_size > _MAX_ENCRYPTED_BUNDLE_BYTES
        or locator.get("kms_key_arn") != key_arn
        or locator.get("format") != "encrypted-database-bundle-v2"
    ):
        _fail("Recovery archive locator does not match the configured target")
    try:
        head = s3_client.head_object(Bucket=bucket, Key=key, VersionId=version_id)
        if (
            head.get("VersionId") != version_id
            or head.get("ServerSideEncryption") != "aws:kms"
            or head.get("SSEKMSKeyId") != key_arn
            or head.get("ContentLength") != expected_size
            or head.get("Metadata", {}).get("sha256") != expected_digest
            or head.get("Metadata", {}).get("format") != "encrypted-database-bundle-v2"
        ):
            _fail("Pinned archive version metadata or KMS encryption does not match the manifest")
        response = s3_client.get_object(Bucket=bucket, Key=key, VersionId=version_id)
    except DatabaseBundleError:
        raise
    except Exception as exc:
        raise DatabaseBundleError("Exact recovery archive version could not be retrieved") from exc
    body = response.get("Body")
    if response.get("VersionId") != version_id or body is None:
        try:
            if body is not None:
                body.close()
        finally:
            _fail("S3 returned a different or unpinned archive version")
    target = Path(destination).expanduser()
    if target.exists() or target.is_symlink() or target.parent.is_symlink() or not target.parent.is_dir():
        body.close()
        _fail("Recovery download target must be a new file in an existing real directory")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    digest = hashlib.sha256()
    count = 0
    try:
        descriptor = os.open(target, flags, 0o600)
        with os.fdopen(descriptor, "wb") as output:
            descriptor = None
            while True:
                block = body.read(1024 * 1024)
                if not block:
                    break
                count += len(block)
                if count > expected_size or count > _MAX_ENCRYPTED_BUNDLE_BYTES:
                    _fail("Downloaded recovery archive exceeds its declared size")
                output.write(block)
                digest.update(block)
            output.flush()
            os.fsync(output.fileno())
        if count != expected_size or digest.hexdigest() != expected_digest:
            _fail("Downloaded recovery archive checksum or size does not match the pinned manifest")
        return target
    except Exception as exc:
        target.unlink(missing_ok=True)
        if isinstance(exc, DatabaseBundleError):
            raise
        raise DatabaseBundleError("Recovery archive download could not be written safely") from exc
    finally:
        body.close()
        if descriptor is not None:
            os.close(descriptor)
