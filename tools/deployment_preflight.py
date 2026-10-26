#!/usr/bin/env python3
"""Read-only deployment configuration checks; never prints secret values."""
import argparse
import math
import os
import stat
import sys
from pathlib import Path


def inspect_environment(env=None):
    env = os.environ if env is None else env
    errors, warnings, passed = [], [], []

    if env.get("ALLOW_UNLINKED_LEGACY_LAW_SEARCH", "").strip() == "1":
        errors.append("ALLOW_UNLINKED_LEGACY_LAW_SEARCH=1 enables unreviewed legacy-law retrieval and is not allowed for deployment.")
    else:
        passed.append("Unlinked legacy-law search override is disabled.")

    token = env.get("ADMIN_TOKEN", "")
    weak_markers = ("change-me", "changeme", "example", "placeholder", "test-token", "your-secret")
    if len(token) < 32 or any(marker in token.lower() for marker in weak_markers):
        errors.append("ADMIN_TOKEN must be a non-placeholder secret of at least 32 characters.")
    else:
        passed.append("ADMIN_TOKEN is present and meets the basic length/placeholder check.")

    raw_score = env.get("MIN_SCORE", "0.3")
    try:
        score = float(raw_score)
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise ValueError
        passed.append("MIN_SCORE is a finite number between 0 and 1.")
    except (TypeError, ValueError):
        errors.append("MIN_SCORE must be a finite number between 0 and 1.")

    # The current application still has a single shared database boundary.
    # Keep this as a release-gate warning until authenticated firm routing,
    # per-firm database selection, and isolation tests are actually shipped.
    warnings.append(
        "This build still uses one shared COPILOT_DB; do not store unrelated firms' "
        "confidential matters until tenant-aware routing, per-firm storage, and "
        "isolation validation are complete."
    )

    raw_db = env.get("COPILOT_DB", "")
    if not raw_db:
        warnings.append("COPILOT_DB is unset; the app defaults to a relative copilot.db path.")
        db_path = Path("copilot.db")
    else:
        db_path = Path(raw_db).expanduser()
        if not db_path.is_absolute():
            warnings.append("COPILOT_DB is relative; production should use an explicit absolute path.")
        else:
            passed.append("COPILOT_DB is explicitly configured as an absolute path.")

    parent = db_path.parent
    if not parent.exists() or not parent.is_dir():
        errors.append("The COPILOT_DB parent directory does not exist or is not a directory.")
    elif not os.access(parent, os.W_OK | os.X_OK):
        errors.append("The COPILOT_DB parent directory is not writable/searchable by this process.")
    else:
        passed.append("The COPILOT_DB parent directory exists and is writable.")

    if db_path.is_symlink():
        # Do not follow a configured database symlink during deployment checks.
        errors.append("COPILOT_DB must not be a symbolic link; configure the actual database file path.")
    elif db_path.exists():
        if not db_path.is_file():
            errors.append("COPILOT_DB exists but is not a regular file.")
        elif not os.access(db_path, os.R_OK | os.W_OK):
            errors.append("COPILOT_DB exists but is not readable and writable by this process.")
        else:
            passed.append("The existing COPILOT_DB file is readable and writable.")
        try:
            mode = stat.S_IMODE(db_path.stat().st_mode)
            if mode & 0o077:
                warnings.append("COPILOT_DB permissions allow group/other access; review and restrict them.")
        except OSError:
            warnings.append("Could not inspect COPILOT_DB file permissions.")
    else:
        warnings.append("COPILOT_DB does not exist yet; this check does not create or initialize it.")

    if os.name == "posix":
        for suffix in ("-wal", "-shm", "-journal"):
            sidecar = Path(str(db_path) + suffix)
            if sidecar.is_symlink():
                errors.append(f"SQLite sidecar {sidecar.name} must not be a symbolic link.")
                continue
            if not sidecar.exists():
                continue
            try:
                sidecar_mode = stat.S_IMODE(sidecar.stat().st_mode)
                if sidecar_mode & 0o077:
                    errors.append(
                        f"SQLite sidecar {sidecar.name} permissions {sidecar_mode:04o} "
                        "allow group/other access."
                    )
            except OSError:
                errors.append(f"Could not inspect SQLite sidecar {sidecar.name} permissions.")

    return passed, warnings, errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero if any warning remains; suitable for a release gate",
    )
    args = parser.parse_args(argv)
    passed, warnings, errors = inspect_environment()

    for item in passed:
        print(f"PASS: {item}")
    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"FAIL: {item}")

    if errors or (args.strict and warnings):
        print("Preflight failed. Resolve the reported issues before deployment.")
        return 1
    if warnings:
        print("Preflight completed with warnings; use --strict for a release gate.")
    else:
        print("Preflight passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
