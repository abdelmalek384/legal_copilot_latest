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
import stat
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
ARABIC_DIGITS = "0-9٠-٩۰-۹"
HEAD = re.compile(
    rf"(?m)^[ \t]*(?:Article|المادة|مادة)[ \t]*:?[ \t]*(?:رقم[ \t]*)?\(?[ \t]*([{ARABIC_DIGITS}]+)(?:[ \t]*(bis(?:[ \t]*\(?[A-Za-z]\)?)?|مكرر))?[ \t]*\)?[ \t]*[:\-]?[ \t]*$",
    re.IGNORECASE,
)
DOCUMENT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")


def _fail(message: str) -> None:
    raise SystemExit("Import bundle rejected: " + message)


def _positive_int_env(name: str, default: int) -> int:
    """Read a positive resource limit from the environment, failing closed on invalid values."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw, 10)
    except (TypeError, ValueError):
        _fail(f"{name} must be a positive integer")
    if value < 1:
        _fail(f"{name} must be a positive integer")
    return value


def _read_regular_file(path: pathlib.Path, label: str, max_bytes: int | None = None) -> bytes:
    """Read one regular file through a stable descriptor; never reopen it by path later."""
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            _fail(f"{label} must be a regular file, not a symbolic link")
        if max_bytes is not None and before.st_size > max_bytes:
            _fail(f"{label} exceeds the configured {max_bytes}-byte size limit")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as source:
            opened = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(opened.st_mode)
                or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
            ):
                _fail(f"{label} changed identity while being opened")
            content = source.read()
            after = os.fstat(source.fileno())
            if max_bytes is not None and len(content) > max_bytes:
                _fail(f"{label} exceeds the configured {max_bytes}-byte size limit")
            if (
                len(content) != after.st_size
                or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns)
                != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
            ):
                _fail(f"{label} changed while being read")
        return content
    except OSError as exc:
        _fail(f"cannot safely read {label}: {type(exc).__name__}")


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
            metadata = json.loads(_read_regular_file(sidecar, "metadata sidecar", max_bytes=1_048_576).decode("utf-8"))
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

        language = metadata.get("language")
        if not isinstance(language, str) or language.strip().lower() not in {"ar", "en", "ar-en"}:
            _fail(f"language must be one of ar, en, or ar-en: {sidecar.name}")
        metadata["language"] = language.strip().lower()
        official_title = metadata.get("official_title")
        if official_title is not None and (
            not isinstance(official_title, str) or not official_title.strip() or len(official_title.strip()) > 300
        ):
            _fail(f"official_title must be a non-empty string of at most 300 characters: {sidecar.name}")
        if isinstance(official_title, str):
            metadata["official_title"] = official_title.strip()

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
            "credential", "api-key", "auth_token", "session_token",
            "x-amz-signature", "x-amz-credential", "x-amz-security-token",
            "x-amz-algorithm", "x-amz-date", "x-amz-expires", "x-amz-signedheaders",
            "x-goog-signature", "x-goog-credential", "x-goog-date", "x-goog-expires",
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
        max_pdf_bytes = _positive_int_env("LEGAL_IMPORT_MAX_PDF_BYTES", 100 * 1024 * 1024)
        pdf_bytes = _read_regular_file(pdf_path, "PDF", max_bytes=max_pdf_bytes)
        if len(pdf_bytes) < 5:
            _fail(f"PDF is empty or too short: {pdf_path.name}")
        if b"%PDF-" not in pdf_bytes[:1024]:
            _fail(f"file does not have a PDF signature in the first 1024 bytes: {pdf_path.name}")
        actual_hash = hashlib.sha256(pdf_bytes).hexdigest()
        if actual_hash.lower() != expected_hash.lower():
            _fail(f"SHA-256 mismatch for {pdf_path.name}")

        prepared.append((sidecar, metadata, pdf_path, pdf_bytes, actual_hash))

    return prepared


def _ocr_language() -> str:
    """Use Arabic+English by default; accept only explicit supported Tesseract language sets."""
    language = os.environ.get("LEGAL_OCR_LANG", "ara+eng").strip().lower()
    if language not in {"ara", "eng", "ara+eng", "eng+ara"}:
        _fail("LEGAL_OCR_LANG must be one of ara, eng, ara+eng, or eng+ara")
    return language


def _ocr(args):
    try:
        import pymupdf
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("OCR dependencies are missing; install requirements-ocr.txt and the Tesseract executable with Arabic and English traineddata.") from exc
    pdf_bytes, page_index = args
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        image_bytes = document[page_index].get_pixmap(dpi=200).tobytes("png")
    return pytesseract.image_to_string(Image.open(io.BytesIO(image_bytes)), lang=_ocr_language())


def page_texts(pdf_bytes, cache_root, content_sha256, cache_key="document"):
    try:
        import pymupdf
    except ImportError as exc:
        raise SystemExit("PyMuPDF is missing; install optional dependencies with: python -m pip install -r requirements-ocr.txt") from exc
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        max_pages = _positive_int_env("LEGAL_IMPORT_MAX_PAGES", 1000)
        if document.page_count > max_pages:
            _fail(f"PDF exceeds the configured {max_pages}-page limit")
        pages = [page.get_text() for page in document]
    joined = "".join(pages)
    if sum(0xE000 <= ord(ch) <= 0xF8FF for ch in joined) > 0.2 * max(len(joined), 1):
        if cache_root.is_symlink() or (cache_root.exists() and not cache_root.is_dir()):
            _fail("OCR cache root must be a regular directory")
        cache_root.mkdir(parents=True, exist_ok=True)
        cache = cache_root / (cache_key + "-" + content_sha256[:16])
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
                cached_page.write_text(_ocr((pdf_bytes, index)), encoding="utf-8")
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
    for sidecar, metadata, pdf_path, pdf_bytes, actual_hash in inputs:
        pages, ocr_used = page_texts(pdf_bytes, output_dir / ".ocr_cache", actual_hash, pdf_path.stem)
        parts = split(clean(pages))
        name = metadata.get("official_title") or NAMES.get(metadata["document_id"], metadata["document_id"])
        language_label = {
            "ar": "Arabic-language source text (official status and authority not yet verified)",
            "en": "English-language text/translation (not authoritative; Arabic original governs when applicable)",
            "ar-en": "Bilingual Arabic/English source text (official status and authority not yet verified)",
        }[metadata["language"]]
        source = (
            f"{metadata['source_url']} | {language_label} "
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
