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
        if raw_root.is_symlink():
            raise ObjectStorageError("object storage root must not be a symbolic link")
        # Resolve trusted parent aliases (for example macOS /var -> /private/var)
        # before creating the root; the configured root itself may never be a link.
        raw_root = raw_root.resolve()
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

    @staticmethod
    def _require_dirfd_support() -> None:
        required = (os.open, os.stat, os.unlink, os.link, os.mkdir)
        if (
            not getattr(os, "O_DIRECTORY", 0)
            or not getattr(os, "O_NOFOLLOW", 0)
            or any(function not in getattr(os, "supports_dir_fd", set()) for function in required)
            or os.stat not in getattr(os, "supports_follow_symlinks", set())
            or os.link not in getattr(os, "supports_follow_symlinks", set())
        ):
            raise ObjectStorageError("local object storage requires no-follow directory-descriptor operations")

    @classmethod
    def _open_directory_chain(cls, path: Path) -> int:
        """Walk an absolute directory path using pinned no-follow descriptors."""
        cls._require_dirfd_support()
        flags = (
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            | getattr(os, "O_CLOEXEC", 0)
        )
        current_fd = os.open(path.anchor, flags)
        try:
            for component in path.parts[1:]:
                next_fd = os.open(component, flags, dir_fd=current_fd)
                os.close(current_fd)
                current_fd = next_fd
            return current_fd
        except Exception:
            os.close(current_fd)
            raise

    def _open_firm_directory(self, firm_id: int, *, create: bool) -> tuple[int, int]:
        firm_id = self._validate_firm_id(firm_id)
        root_fd = self._open_directory_chain(self.root)
        namespace_fd = None
        name = "firm-" + str(firm_id)
        try:
            if create:
                try:
                    os.mkdir(name, mode=0o700, dir_fd=root_fd)
                except FileExistsError:
                    pass
            flags = (
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                | getattr(os, "O_CLOEXEC", 0)
            )
            namespace_fd = os.open(name, flags, dir_fd=root_fd)
            metadata = os.fstat(namespace_fd)
            if not stat.S_ISDIR(metadata.st_mode):
                raise ObjectStorageError("firm storage namespace is unavailable")
            if os.name == "posix":
                os.fchmod(namespace_fd, 0o700)
            return root_fd, namespace_fd
        except OSError as exc:
            if namespace_fd is not None:
                os.close(namespace_fd)
            os.close(root_fd)
            raise ObjectStorageError("firm storage namespace is unavailable or unsafe") from exc
        except Exception:
            if namespace_fd is not None:
                os.close(namespace_fd)
            os.close(root_fd)
            raise

    @staticmethod
    def _close_directory_descriptors(root_fd: int, namespace_fd: int) -> None:
        os.close(namespace_fd)
        os.close(root_fd)

    @staticmethod
    def _stat_at(directory_fd: int, name: str):
        try:
            return os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            return None

    @staticmethod
    def _fsync_directory_fd(directory_fd: int) -> None:
        if os.name == "posix":
            os.fsync(directory_fd)

    def stage(self, firm_id: int, data: bytes) -> StagedObject:
        """Write bytes to a new private staging object through a pinned namespace."""
        self._validate_firm_id(firm_id)
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        if len(data) > self.max_bytes:
            raise ObjectStorageError("object exceeds configured size limit")
        object_id = uuid.uuid4().hex
        staged_name = object_id + ".staged"
        final_name = object_id + ".blob"
        root_fd, namespace_fd = self._open_firm_directory(firm_id, create=True)
        descriptor = None
        created = False
        try:
            if self._stat_at(namespace_fd, final_name) is not None:
                raise ObjectStorageError("object ID collision")
            flags = (
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
                | getattr(os, "O_CLOEXEC", 0)
            )
            descriptor = os.open(staged_name, flags, 0o600, dir_fd=namespace_fd)
            created = True
            with os.fdopen(descriptor, "wb", closefd=True) as handle:
                descriptor = None
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            staged_info = self._stat_at(namespace_fd, staged_name)
            if staged_info is None or not stat.S_ISREG(staged_info.st_mode) or staged_info.st_nlink != 1:
                raise ObjectStorageError("staged object changed while being written")
            if self._stat_at(namespace_fd, final_name) is not None:
                raise ObjectStorageError("object ID collision")
            self._fsync_directory_fd(namespace_fd)
        except Exception as exc:
            if descriptor is not None:
                os.close(descriptor)
            if created:
                try:
                    os.unlink(staged_name, dir_fd=namespace_fd)
                except OSError:
                    pass
            if isinstance(exc, ObjectStorageError):
                raise
            raise ObjectStorageError("could not stage object safely") from exc
        finally:
            self._close_directory_descriptors(root_fd, namespace_fd)
        return StagedObject(object_id, hashlib.sha256(data).hexdigest(), len(data))

    def finalize(self, firm_id: int, object_id: str) -> None:
        """Atomically publish a staged object without following or replacing paths."""
        object_id = self._validate_object_id(object_id)
        staged_name = object_id + ".staged"
        final_name = object_id + ".blob"
        root_fd, namespace_fd = self._open_firm_directory(firm_id, create=False)
        try:
            before = self._stat_at(namespace_fd, staged_name)
            if before is None or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise ObjectStorageError("staged object does not exist or is not a regular file")
            if self._stat_at(namespace_fd, final_name) is not None:
                raise ObjectStorageError("final object already exists")
            os.link(
                staged_name, final_name,
                src_dir_fd=namespace_fd, dst_dir_fd=namespace_fd,
                follow_symlinks=False,
            )
            linked = self._stat_at(namespace_fd, final_name)
            after = self._stat_at(namespace_fd, staged_name)
            if (
                linked is None or not stat.S_ISREG(linked.st_mode) or linked.st_nlink != 2
                or (linked.st_dev, linked.st_ino) != (before.st_dev, before.st_ino)
                or after is None or not stat.S_ISREG(after.st_mode) or after.st_nlink != 2
                or (after.st_dev, after.st_ino) != (before.st_dev, before.st_ino)
            ):
                try:
                    os.unlink(final_name, dir_fd=namespace_fd)
                except OSError:
                    pass
                raise ObjectStorageError("staged object changed while finalizing")
            os.unlink(staged_name, dir_fd=namespace_fd)
            published = self._stat_at(namespace_fd, final_name)
            if published is None or not stat.S_ISREG(published.st_mode) or published.st_nlink != 1:
                try:
                    os.unlink(final_name, dir_fd=namespace_fd)
                except OSError:
                    pass
                raise ObjectStorageError("final object has an unexpected hard-link count")
            self._fsync_directory_fd(namespace_fd)
        except FileExistsError as exc:
            raise ObjectStorageError("final object already exists") from exc
        except OSError as exc:
            raise ObjectStorageError("could not finalize object safely") from exc
        finally:
            self._close_directory_descriptors(root_fd, namespace_fd)

    def open(self, firm_id: int, object_id: str) -> BinaryIO:
        """Open a finalized regular file relative to a pinned firm namespace."""
        object_id = self._validate_object_id(object_id)
        root_fd, namespace_fd = self._open_firm_directory(firm_id, create=False)
        descriptor = None
        try:
            flags = (
                os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
                | getattr(os, "O_CLOEXEC", 0)
            )
            descriptor = os.open(object_id + ".blob", flags, dir_fd=namespace_fd)
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise ObjectStorageError("stored object is not a single-link regular file")
            handle = os.fdopen(descriptor, "rb", closefd=True)
            descriptor = None
            return handle
        except OSError as exc:
            raise ObjectStorageError("object is unavailable or unsafe") from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)
            self._close_directory_descriptors(root_fd, namespace_fd)

    def object_presence(self, firm_id: int, object_id: str) -> tuple[bool, bool]:
        """Return staged/final presence without following namespace or object links."""
        object_id = self._validate_object_id(object_id)
        root_fd, namespace_fd = self._open_firm_directory(firm_id, create=False)
        try:
            presence = []
            for name in (object_id + ".staged", object_id + ".blob"):
                metadata = self._stat_at(namespace_fd, name)
                if metadata is not None and (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1):
                    raise ObjectStorageError("stored object is not a single-link regular file")
                presence.append(metadata is not None)
            return presence[0], presence[1]
        finally:
            self._close_directory_descriptors(root_fd, namespace_fd)

    def _verify_object(
        self, firm_id: int, object_id: str, state: str, *,
        expected_sha256: str, expected_size: int,
    ) -> bool:
        if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
            raise ValueError("expected_sha256 must be a lowercase SHA-256 digest")
        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
            raise ValueError("expected_size must be a non-negative integer")
        if expected_size > self.max_bytes:
            raise ValueError("expected_size exceeds the configured object size limit")
        object_id = self._validate_object_id(object_id)
        if state not in {"staged", "blob"}:
            raise ValueError("invalid object state")
        root_fd, namespace_fd = self._open_firm_directory(firm_id, create=False)
        descriptor = None
        try:
            flags = (
                os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
                | getattr(os, "O_CLOEXEC", 0)
            )
            descriptor = os.open(object_id + "." + state, flags, dir_fd=namespace_fd)
            metadata = os.fstat(descriptor)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1 or metadata.st_size > self.max_bytes:
                return False
            digest = hashlib.sha256()
            size = 0
            with os.fdopen(descriptor, "rb", closefd=True) as handle:
                descriptor = None
                while True:
                    block = handle.read(min(1024 * 1024, self.max_bytes - size + 1))
                    if not block:
                        break
                    size += len(block)
                    if size > self.max_bytes:
                        return False
                    digest.update(block)
            return size == expected_size and digest.hexdigest() == expected_sha256
        except OSError:
            return False
        finally:
            if descriptor is not None:
                os.close(descriptor)
            self._close_directory_descriptors(root_fd, namespace_fd)

    def verify(self, firm_id: int, object_id: str, *, expected_sha256: str, expected_size: int) -> bool:
        """Verify finalized bytes against database metadata without changing them."""
        return self._verify_object(
            firm_id, object_id, "blob",
            expected_sha256=expected_sha256, expected_size=expected_size,
        )

    def verify_staged(
        self, firm_id: int, object_id: str, *, expected_sha256: str, expected_size: int
    ) -> bool:
        """Verify staged bytes against database metadata without publishing them."""
        return self._verify_object(
            firm_id, object_id, "staged",
            expected_sha256=expected_sha256, expected_size=expected_size,
        )

    def delete(self, firm_id: int, object_id: str) -> bool:
        """Delete staged/final names relative to a pinned namespace; caller enforces holds."""
        object_id = self._validate_object_id(object_id)
        root_fd, namespace_fd = self._open_firm_directory(firm_id, create=False)
        removed = False
        try:
            for name in (object_id + ".staged", object_id + ".blob"):
                metadata = self._stat_at(namespace_fd, name)
                if metadata is None:
                    continue
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                    raise ObjectStorageError("stored object is not a single-link regular file")
                os.unlink(name, dir_fd=namespace_fd)
                removed = True
            if removed:
                self._fsync_directory_fd(namespace_fd)
            return removed
        except OSError as exc:
            raise ObjectStorageError("could not delete object safely") from exc
        finally:
            self._close_directory_descriptors(root_fd, namespace_fd)
