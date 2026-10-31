#!/usr/bin/env python3
"""Read-only validator for required database operational release evidence."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.database_release_acceptance import load_acceptance_manifest, original_storage_config_fingerprint


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Controlled operational acceptance manifest outside the repository.")
    parser.add_argument(
        "--print-storage-config-fingerprint",
        action="store_true",
        help="print the non-secret fingerprint of the configured S3/KMS target and exit",
    )
    args = parser.parse_args(argv)
    if args.print_storage_config_fingerprint:
        fingerprint = original_storage_config_fingerprint()
        if fingerprint is None:
            parser.error(
                "configure distinct original-object and recovery-archive S3 buckets, regions, and KMS keys before computing the fingerprint"
            )
        print(fingerprint)
        return 0
    report = load_acceptance_manifest(
        args.manifest,
        expected_storage_config_sha256=original_storage_config_fingerprint() or "",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2) + "\n", end="")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
