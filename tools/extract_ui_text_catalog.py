#!/usr/bin/env python3
"""Extract literal Arabic/English uiText() pairs into a reviewable CSV catalog.

Dynamic uiText() arguments are intentionally skipped: they need a human-authored
translation or a separate runtime key, not guessed extraction.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "static" / "index.html"
DEFAULT_OUTPUT = ROOT / "static" / "i18n" / "ui_text_pairs.csv"
_STRING = r"""'(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*'"""
_PAIR_RE = re.compile(
    r"\\buiText\\s*\\(\\s*(" + _STRING + r")\\s*,\\s*(" + _STRING + r")\\s*\\)"
)
_CALL_RE = re.compile(r"\\buiText\\s*\\(")


def decode_js_string(literal: str) -> str:
    """Decode the common JavaScript string escapes without corrupting Unicode."""
    body = literal[1:-1]
    out: list[str] = []
    index = 0
    escapes = {"n": "\\n", "r": "\\r", "t": "\\t", "b": "\\b", "f": "\\f",
               "v": "\\v", "0": "\\0", "\\\\": "\\\\", "'": "'", '"': '"', "/": "/"}
    while index < len(body):
        char = body[index]
        if char != "\\\\":
            out.append(char)
            index += 1
            continue
        index += 1
        if index >= len(body):
            break
        escaped = body[index]
        if escaped in {"\\n", "\\r"}:
            if escaped == "\\r" and index + 1 < len(body) and body[index + 1] == "\\n":
                index += 1
            index += 1
            continue
        if escaped == "u":
            if index + 1 < len(body) and body[index + 1] == "{":
                end = body.find("}", index + 2)
                if end >= 0:
                    out.append(chr(int(body[index + 2:end], 16)))
                    index = end + 1
                    continue
            digits = body[index + 1:index + 5]
            if len(digits) == 4 and all(c in "0123456789abcdefABCDEF" for c in digits):
                out.append(chr(int(digits, 16)))
                index += 5
                continue
        if escaped == "x":
            digits = body[index + 1:index + 3]
            if len(digits) == 2 and all(c in "0123456789abcdefABCDEF" for c in digits):
                out.append(chr(int(digits, 16)))
                index += 3
                continue
        out.append(escapes.get(escaped, escaped))
        index += 1
    return "".join(out)


def extract_pairs(source: str) -> tuple[list[tuple[str, str, int]], int, int]:
    """Return unique literal pairs, total literal occurrences, and dynamic call count."""
    counts: OrderedDict[tuple[str, str], int] = OrderedDict()
    for match in _PAIR_RE.finditer(source):
        arabic = decode_js_string(match.group(1))
        english = decode_js_string(match.group(2))
        if arabic.strip() and english.strip():
            pair = (arabic, english)
            counts[pair] = counts.get(pair, 0) + 1
    total_calls = len(_CALL_RE.findall(source))
    literal_calls = sum(counts.values())
    return (
        [(arabic, english, count) for (arabic, english), count in counts.items()],
        literal_calls,
        max(0, total_calls - literal_calls),
    )


def render_catalog(pairs: list[tuple[str, str, int]]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\\n")
    writer.writerow(["arabic", "english", "occurrences"])
    writer.writerows(pairs)
    return stream.getvalue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the checked-in catalog is stale.")
    args = parser.parse_args(argv)
    pairs, literal_calls, dynamic_calls = extract_pairs(args.source.read_text(encoding="utf-8"))
    rendered = render_catalog(pairs)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            print("UI text catalog is stale; regenerate with tools/extract_ui_text_catalog.py.", file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="")
    print(
        f"Extracted {literal_calls} literal uiText() occurrences into {len(pairs)} unique pairs; "
        f"skipped {dynamic_calls} dynamic calls."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
