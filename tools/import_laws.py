"""Turn downloaded law PDFs (+ their .json metadata files) into article-level candidate rows.

Usage: python tools/import_laws.py source_dir output_dir
Install optional extraction dependencies with:
    python -m pip install -r requirements-ocr.txt

This tool verifies local file integrity and provenance-field shape only. It does
not establish source authenticity, reuse permission, legal force, or completeness.
"""
from __future__ import annotations

import collections
import hashlib
import io
import json
import os
import pathlib
import re
import sys
from datetime import date, datetime
from urllib.parse import parse_qsl, urlsplit

NAMES = {
    "penal_code_58_1937_en": "Penal Code (Law No. 58 of 1937)",
    "banking_law_88_2003_en": "Central Bank, Banking Sector and Money Law (Law No. 88 of 2003)",
    "investment_law_72_2017": "Investment Law (Law No. 72 of 2017)",
    "companies_law_159_1981_en": "Companies Law (Law No. 159 of 1981)",
    "income_tax_law_91_2005_en": "Income Tax Law (Law No. 91 of 2005)",
    "env_regs_pm_decree_338_1995_en": "Executive Regulations of Environment Law 4/1994 (PM Decree 338 of 1995)",
}
HEAD = re.compile(r"(?m)^[ \t]*Article[ \t]*:?[ \t]*\(?[ \t]*(\d+)(?:[ \t]*(bis(?:[ \t]*\(?[A-Za-z]\)?)?))?[ \t]*\)?[ \t]*[:\-]?[ \t]*$")
DOCUMENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def _fail(message: str) -> None:
    raise SystemExit("Import bundle rejected: " + message)


def _sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def _valid_retrieval_date(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    raw = value.strip()
    try:
        datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return True
    except ValueError:
        try:
            date.fromisoformat(raw)
            return True
        except ValueError:
            return False


def validate_inputs(src: str | pathlib.Path, out: str | pathlib.Path):
    """Validate every sidecar/PDF pair before extraction or output writes."""
    source_dir = pathlib.Path(src)
    output_dir = pathlib.Path(out)
    if source_dir.is_symlink() or not source_dir.is_dir():
        _fail("source directory must be an existing regular directory, not a symbolic link")
    if output_dir.is_symlink():
        _fail("output directory must not be a symbolic link")
    if output_dir.exists() and not output_dir.is_dir():
        _fail("output path must be a directory")
    if output_dir.exists():
        for name in ("law_rows.jsonl", "import_report.md", ".ocr_cache"):
            existing = output_dir / name
            if existing.is_symlink():
                _fail(f"output path must not be a symbolic link: {name}")
            if existing.exists() and name == ".ocr_cache" and not existing.is_dir():
                _fail("OCR cache path must be a directory")
            if existing.exists() and name != ".ocr_cache" and not existing.is_file():
                _fail(f"output file path is not a regular file: {name}")
    source_resolved = source_dir.resolve()
    output_resolved = output_dir.resolve()
    if source_resolved == output_resolved or source_resolved in output_resolved.parents:
        _fail("output directory must be separate from and outside the source directory")

    sidecars = sorted(source_dir.glob("*.json"))
    if not sidecars:
        _fail("no JSON metadata sidecars were found")
    pdfs = sorted(source_dir.glob("*.pdf"))
    sidecar_stems = {item.stem.lower() for item in sidecars}
    pdf_stems = {item.stem.lower() for item in pdfs}
    if sidecar_stems != pdf_stems:
        missing_pdf = sorted(sidecar_stems - pdf_stems)
        missing_sidecar = sorted(pdf_stems - sidecar_stems)
        _fail(f"PDF/sidecar pairs do not match (missing PDFs: {missing_pdf}; missing sidecars: {missing_sidecar})")

    prepared = []
    seen_ids = set()
    for sidecar in sidecars:
        if sidecar.is_symlink() or not sidecar.is_file():
            _fail(f"metadata sidecar must be a regular file, not a symbolic link: {sidecar.name}")
        try:
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            _fail(f"invalid JSON sidecar {sidecar.name}: {type(exc).__name__}")
        if not isinstance(metadata, dict):
            _fail(f"metadata sidecar must contain a JSON object: {sidecar.name}")

        document_id = metadata.get("document_id")
        if not isinstance(document_id, str) or not DOCUMENT_ID.fullmatch(document_id):
            _fail(f"invalid or missing document_id in {sidecar.name}")
        normalized_id = document_id.casefold()
        if normalized_id in seen_ids:
            _fail(f"duplicate document_id: {document_id}")
        seen_ids.add(normalized_id)

        source_url = metadata.get("source_url")
        try:
            parsed_url = urlsplit(source_url) if isinstance(source_url, str) else None
            if parsed_url is not None:
                _ = parsed_url.port
        except ValueError:
            parsed_url = None
        if (
            parsed_url is None
            or parsed_url.scheme.lower() != "https"
            or not parsed_url.hostname
            or parsed_url.username
            or parsed_url.password
            or parsed_url.fragment
        ):
            _fail(f"source_url must be an HTTPS URL without credentials or fragment: {sidecar.name}")
        sensitive_query_keys = {
            "token", "access_token", "auth", "authorization", "password", "secret",
            "signature", "sig", "api_key", "apikey", "session", "sessionid",
            "credential", "x-amz-signature", "x-amz-credential", "x-amz-security-token",
        }
        query_keys = {key.casefold() for key, _ in parse_qsl(parsed_url.query, keep_blank_values=True)}
        if query_keys & sensitive_query_keys:
            _fail(f"source_url must not contain signed or credential query parameters: {sidecar.name}")

        if not _valid_retrieval_date(metadata.get("retrieved_at")):
            _fail(f"retrieved_at must be an ISO date or datetime: {sidecar.name}")

        expected_hash = metadata.get("content_sha256")
        if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash):
            _fail(f"content_sha256 must be a full 64-character SHA-256: {sidecar.name}")

        pdf_path = sidecar.with_suffix(".pdf")
        if pdf_path.is_symlink() or not pdf_path.is_file():
            _fail(f"PDF must be a regular file, not a symbolic link: {pdf_path.name}")
        if pdf_path.stat().st_size < 5:
            _fail(f"PDF is empty or too short: {pdf_path.name}")
        with pdf_path.open("rb") as pdf_file:
            if b"%PDF-" not in pdf_file.read(1024):
                _fail(f"file does not have a PDF signature in the first 1024 bytes: {pdf_path.name}")
        actual_hash = _sha256_file(pdf_path)
        if actual_hash.lower() != expected_hash.lower():
            _fail(f"SHA-256 mismatch for {pdf_path.name}")

        prepared.append((sidecar, metadata, pdf_path, actual_hash))

    return prepared


def _ocr(args):
    try:
        import pymupdf
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("OCR dependencies are missing; install requirements-ocr.txt and the Tesseract executable.") from exc
    path, page_index = args
    with pymupdf.open(path) as document:
        image_bytes = document[page_index].get_pixmap(dpi=130).tobytes("png")
    return pytesseract.image_to_string(Image.open(io.BytesIO(image_bytes)), lang="eng")


def page_texts(path, cache_root, content_sha256):
    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is missing; install optional dependencies with: python -m pip install -r requirements-ocr.txt") from exc
    with pymupdf.open(path) as document:
        pages = [page.get_text() for page in document]
    joined = "".join(pages)
    if sum(0xE000 <= ord(ch) <= 0xF8FF for ch in joined) > 0.2 * max(len(joined), 1):
        if cache_root.is_symlink() or (cache_root.exists() and not cache_root.is_dir()):
            _fail("OCR cache root must be a regular directory")
        cache_root.mkdir(parents=True, exist_ok=True)
        cache = cache_root / (path.stem + "-" + content_sha256[:16])
        if cache.is_symlink() or (cache.exists() and not cache.is_dir()):
            _fail("per-document OCR cache must be a regular directory")
        cache.mkdir(parents=True, exist_ok=True)
        budget = int(os.environ.get("OCR_BATCH", 10 ** 9))
        output = []
        for index in range(len(pages)):
            cached_page = cache / ("%d.txt" % index)
            if cached_page.is_symlink() or (cached_page.exists() and not cached_page.is_file()):
                _fail("OCR cache page must be a regular file: " + cached_page.name)
            if not cached_page.exists():
                if budget <= 0:
                    raise SystemExit("OCR in progress (%d/%d pages done): run again" % (index, len(pages)))
                cached_page.write_text(_ocr((str(path), index)), encoding="utf-8")
                budget -= 1
            if cached_page.stat().st_size == 0:
                _fail("OCR cache page is empty: " + cached_page.name)
            output.append(cached_page.read_text(encoding="utf-8"))
        return output, True
    return pages, False


def clean(pages):
    lines = [line.strip() for text in pages for line in text.replace("\r", "\n").split("\n")]
    frequency = collections.Counter(line for line in lines if line)
    drop = {line for line, count in frequency.items() if count > 12 and 8 <= len(line) < 80 and not HEAD.match(line)}
    keep = [line for line in lines if line not in drop and not re.fullmatch(r"(Page\s*\|\s*)?\d{1,4}|First draft", line)]
    return "\n".join(keep)


def split(text):
    matches = list(HEAD.finditer(text))
    rows, block, previous = [], 1, 0
    preamble = text[:matches[0].start()] if matches else text
    if preamble.strip():
        rows.append(("preamble", 0, preamble))
    for index, match in enumerate(matches):
        number = int(match.group(1))
        if number < previous:
            block += 1
        previous = number
        rows.append((
            match.group(1) + (" " + match.group(2) if match.group(2) else ""),
            block,
            text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)],
        ))
    return rows


def pieces(text, size=8000):
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n\n", text)).strip()
    while len(text) > size:
        boundary = text.rfind(" ", 0, size)
        boundary = boundary if boundary > 0 else size
        yield text[:boundary]
        text = text[boundary:].lstrip()
    if text:
        yield text


def main(src, out):
    inputs = validate_inputs(src, out)
    output_dir = pathlib.Path(out)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []
    report = ["# Import report", ""]
    for sidecar, metadata, pdf_path, actual_hash in inputs:
        pages, ocr_used = page_texts(pdf_path, output_dir / ".ocr_cache", actual_hash)
        parts = split(clean(pages))
        name = NAMES.get(metadata["document_id"], metadata["document_id"])
        source = (
            f"{metadata['source_url']} | English translation (not authoritative; the Arabic original governs) "
            f"| retrieved {metadata['retrieved_at'][:10]} | sha256 {actual_hash}"
            + (" | text recovered by OCR" if ocr_used else "")
        )
        blocks = collections.defaultdict(list)
        row_count = 0
        for article, block, body in parts:
            for text in pieces(body):
                all_rows.append({
                    "law": name + ("" if block <= 1 else " [block %d]" % block),
                    "article": article,
                    "text": text,
                    "as_of": None,
                    "in_force": 0,
                    "verified": 0,
                    "source": source,
                })
                row_count += 1
            blocks[block].append(article)

        report += [
            f"## {name}",
            f"- file: {pdf_path.name} | pages: {len(pages)} | OCR used: {ocr_used} | rows: {row_count}",
            f"- source_url: {metadata['source_url']}",
            f"- retrieved_at: {metadata['retrieved_at']}",
            f"- verified PDF SHA-256: {actual_hash}",
            f"- review_status metadata: {metadata.get('review_status', 'not_recorded')}",
            "",
            "| block | first | last | articles found | missing numbers in range |",
            "|---|---|---|---|---|",
        ]
        for block, articles in sorted(blocks.items()):
            numbers = sorted({int(article.split()[0]) for article in articles if article[0].isdigit()})
            missing = sorted(set(range(numbers[0], numbers[-1] + 1)) - set(numbers)) if numbers else []
            report.append(
                "| %s | %s | %s | %d | %d %s |"
                % ("preamble" if block == 0 else block, numbers[0] if numbers else "-", numbers[-1] if numbers else "-", len(articles), len(missing), missing[:12] if missing else "")
            )
        short_rows = sum(1 for row in all_rows if row["source"] == source and len(row["text"]) < 40)
        report += ["", f"- very short rows (<40 chars, check for splitting errors): {short_rows}", ""]

    (output_dir / "law_rows.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in all_rows) + "\n",
        encoding="utf-8",
    )
    (output_dir / "import_report.md").write_text("\n".join(report), encoding="utf-8")
    print("rows:", len(all_rows))
    print("\n".join(report))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python tools/import_laws.py source_dir output_dir")
    main(sys.argv[1], sys.argv[2])
