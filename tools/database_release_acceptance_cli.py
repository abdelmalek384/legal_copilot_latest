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

from tools.database_release_acceptance import load_acceptance_manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Controlled operational acceptance manifest outside the repository.")
    args = parser.parse_args(argv)
    report = load_acceptance_manifest(args.manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2) + "\n", end="")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
