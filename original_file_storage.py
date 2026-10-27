"""Private, tenant-namespaced local object storage for original matter files.

This adapter is intended for development and isolated testing. It is not a
production S3/KMS implementation and does not replace application authorization.
Callers must pass a firm ID resolved from authenticated server-side context.
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


_OBJECT_ID_RE = re.compile(r"^[0-9a-f]{32}$")


class ObjectStorageError(RuntimeError):
    """Raised when an object cannot be safely stored or retrieved."""


@dataclass(frozen=True)
class StagedObject:
    object_id: str
    sha256: str
    byte_size: int


class LocalPrivateObjectStore:
    """Filesystem adapter with private permissions and opaque object IDs.

    Request-supplied filenames and storage keys are never accepted. Firm IDs
    must come from trusted server-side authorization, not request payloads.
    """

    def __init__(self, root: str | os.PathLike[str], *, max_bytes: int = 15_000_000):
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
            raise ValueError("max_bytes must be a positive integer")
        raw_root = Path(root).expanduser().absolute()
        self._reject_symlink_components(raw_root)
        try:
            raw_root.mkdir(parents=True, mode=0o700, exist_ok=True)
            if raw_root.is_symlink() or not raw_root.is_dir():
                raise ObjectStorageError("object storage root must be a real directory")
            if os.name == "posix":
                raw_root.chmod(0o700)
        except OSError as exc:
            raise ObjectStorageError("object storage root is unavailable") from exc
        self.root = raw_root
        self.max_bytes = max_bytes

    @staticmethod
    def _reject_symlink_components(path: Path) -> None:
        current = Path(path.anchor)
        for part in path.parts[1:]:
            current = current / part
            try:
                mode = current.lstat().st_mode
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise ObjectStorageError("cannot verify object storage path") from exc
            if stat.S_ISLNK(mode):
                raise ObjectStorageError("symbolic links are not allowed in object storage paths")

    @staticmethod
    def _validate_firm_id(firm_id: int) -> int:
        if isinstance(firm_id, bool) or not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("trusted firm_id must be a positive integer")
        return firm_id

    @staticmethod
    def _validate_object_id(object_id: str) -> str:
        if not isinstance(object_id, str) or not _OBJECT_ID_RE.fullmatch(object_id):
            raise ValueError("invalid opaque object ID")
        return object_id

    def _firm_dir(self, firm_id: int, *, create: bool) -> Path:
        firm_id = self._validate_firm_id(firm_id)
        directory = self.root / ("firm-" + str(firm_id))
        try:
            if directory.is_symlink():
                raise ObjectStorageError("firm storage namespace must not be a symbolic link")
            if create:
                directory.mkdir(mode=0o700, exist_ok=True)
            if not directory.is_dir() or directory.is_symlink():
                raise ObjectStorageError("firm storage namespace is unavailable")
            if os.name == "posix":
                directory.chmod(0o700)
            return directory
        except OSError as exc:
            raise ObjectStorageError("firm storage namespace is unavailable") from exc

    def _paths(self, firm_id: int, object_id: str, *, create_dir: bool = False) -> tuple[Path, Path]:
        object_id = self._validate_object_id(object_id)
        directory = self._firm_dir(firm_id, create=create_dir)
        staged = directory / (object_id + ".staged")
        final = directory / (object_id + ".blob")
        for path in (staged, final):
            if path.is_symlink():
                raise ObjectStorageError("stored objects must not be symbolic links")
        return staged, final

    def stage(self, firm_id: int, data: bytes) -> StagedObject:
        """Write bytes to a new private staging object and return its digest."""
        self._validate_firm_id(firm_id)
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if len(data) > self.max_bytes:
            raise ObjectStorageError("object exceeds configured size limit")
        object_id = uuid.uuid4().hex
        staged, final = self._paths(firm_id, object_id, create_dir=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        fd = None
        try:
            fd = os.open(staged, flags, 0o600)
            with os.fdopen(fd, "wb", closefd=True) as handle:
                fd = None
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if final.exists() or final.is_symlink():
                raise ObjectStorageError("object ID collision")
        except Exception as exc:
            if fd is not None:
                os.close(fd)
            try:
                staged.unlink(missing_ok=True)
            except OSError:
                pass
            if isinstance(exc, ObjectStorageError):
                raise
            raise ObjectStorageError("could not stage object safely") from exc
        return StagedObject(object_id, hashlib.sha256(data).hexdigest(), len(data))

    def finalize(self, firm_id: int, object_id: str) -> None:
        """Atomically publish a staged object without overwriting an existing one."""
        staged, final = self._paths(firm_id, object_id)
        if not staged.is_file() or staged.is_symlink():
            raise ObjectStorageError("staged object does not exist")
        if final.exists() or final.is_symlink():
            raise ObjectStorageError("final object already exists")
        try:
            # Hard-link creation fails if final already exists; both names stay
            # on the same filesystem, so the visible object is never partial.
            os.link(staged, final, follow_symlinks=False)
            staged.unlink()
            self._fsync_directory(final.parent)
        except FileExistsError as exc:
            raise ObjectStorageError("final object already exists") from exc
        except OSError as exc:
            raise ObjectStorageError("could not finalize object safely") from exc

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        if os.name != "posix":
            return
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        fd = os.open(directory, flags)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def open(self, firm_id: int, object_id: str) -> BinaryIO:
        """Open a finalized object without following symbolic links."""
        _, final = self._paths(firm_id, object_id)
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        try:
            fd = os.open(final, flags)
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode):
                os.close(fd)
                raise ObjectStorageError("stored object is not a regular file")
            return os.fdopen(fd, "rb", closefd=True)
        except OSError as exc:
            raise ObjectStorageError("object is unavailable") from exc

    def verify(self, firm_id: int, object_id: str, *, expected_sha256: str, expected_size: int) -> bool:
        """Verify finalized bytes against database metadata without changing them."""
        if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise ValueError("expected_sha256 must be a lowercase SHA-256 digest")
        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
            raise ValueError("expected_size must be a non-negative integer")
        digest = hashlib.sha256()
        size = 0
        try:
            with self.open(firm_id, object_id) as handle:
                while True:
                    block = handle.read(1024 * 1024)
                    if not block:
                        break
                    size += len(block)
                    digest.update(block)
        except ObjectStorageError:
            return False
        return size == expected_size and digest.hexdigest() == expected_sha256

    def delete(self, firm_id: int, object_id: str) -> bool:
        """Delete a staged or finalized object; callers must enforce hold policy."""
        staged, final = self._paths(firm_id, object_id)
        removed = False
        try:
            for path in (staged, final):
                if path.is_symlink():
                    raise ObjectStorageError("stored objects must not be symbolic links")
                try:
                    path.unlink()
                    removed = True
                except FileNotFoundError:
                    pass
            if removed:
                self._fsync_directory(final.parent)
            return removed
        except OSError as exc:
            raise ObjectStorageError("could not delete object safely") from exc
