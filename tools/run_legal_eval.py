#!/usr/bin/env python3
"""Run questions against the authenticated Legal Copilot API and save evaluation rows.

This runner only searches the verified legal corpus; it never supplies a case ID or
matter documents. It does not calculate scores. Configure a local/approved model
endpoint in the application if generated answers are desired.
"""
import argparse
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse
from pathlib import Path


class RunnerError(RuntimeError):
    pass


MAX_API_RESPONSE_BYTES = 16 * 1024 * 1024


def validate_base_url(base_url, allow_remote=False):
    if (
        not isinstance(base_url, str)
        or not base_url
        or base_url != base_url.strip()
        or any(ch.isspace() or ord(ch) < 32 for ch in base_url)
    ):
        raise RunnerError("base URL must not contain whitespace and must be a valid HTTP(S) URL")
    try:
        parsed = urlparse(base_url)
        port = parsed.port  # Accessing .port rejects non-numeric and out-of-range ports.
        host = parsed.hostname
    except (ValueError, TypeError) as exc:
        raise RunnerError("base URL must be a well-formed HTTP(S) URL with a valid port") from exc
    if parsed.username is not None or parsed.password is not None:
        raise RunnerError("base URL must not contain embedded credentials")
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not host
        or parsed.netloc.endswith(":")
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise RunnerError("base URL must be a valid HTTP(S) URL with a valid port")
    if parsed.query or parsed.fragment:
        raise RunnerError("base URL must not contain a query string or fragment")
    host = host.lower()
    loopback = host in {"localhost", "127.0.0.1", "::1"}
    if not loopback and not allow_remote:
        raise RunnerError("non-local API targets require the explicit --allow-remote flag")
    if not loopback and parsed.scheme.lower() != "https":
        raise RunnerError("remote evaluation targets must use HTTPS")
    return base_url.rstrip("/")


def read_questions(path, limit=None):
    rows = []
    seen = set()
    for line_no, raw in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RunnerError(f"{path}:{line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"].strip():
            raise RunnerError(f"{path}:{line_no}: each question needs a non-empty id")
        if row["id"] in seen:
            raise RunnerError(f"{path}:{line_no}: duplicate question id {row['id']}")
        if not isinstance(row.get("question_ar"), str) or len(row["question_ar"].strip()) < 2:
            raise RunnerError(f"{path}:{line_no}: question_ar must contain at least two characters")
        seen.add(row["id"])
        rows.append(row)
    if limit is not None:
        if limit < 1:
            raise RunnerError("--limit must be positive")
        rows = rows[:limit]
    if not rows:
        raise RunnerError("no questions found")
    return rows


def _pin_cite(hit):
    article = str(hit.get("article") or "").strip()
    if article:
        if re.search(r"(?:المادة|مادة|article|art\.?)", article, re.I):
            return article
        return "المادة " + article
    page = str(hit.get("page") or "").strip()
    if page:
        return "صفحة " + page
    return None


def _mask_markdown_code(answer):
    """Mask Markdown code and hidden HTML comments before extracting citation markers."""
    if not isinstance(answer, str):
        return ""
    answer = re.sub(
        r"<!--.*?(?:-->|$)",
        lambda match: re.sub(r"[^\r\n]", " ", match.group(0)),
        answer,
        flags=re.S,
    )
    output = []
    fence_char = None
    fence_length = 0
    for line in answer.splitlines(keepends=True):
        stripped = line.lstrip(" \t")
        if fence_char is not None:
            output.append(re.sub(r"[^\r\n]", " ", line))
            close = re.match(
                r"^" + re.escape(fence_char) + r"{" + str(fence_length) + r",}[ \t]*\r?\n?$",
                stripped,
            )
            if close:
                fence_char = None
                fence_length = 0
            continue
        opening = re.match(r"^(\u0060{3,}|~{3,})(?:[^\r\n]*)?(?:\r?\n)?$", stripped)
        if opening:
            fence_char = opening.group(1)[0]
            fence_length = len(opening.group(1))
            output.append(re.sub(r"[^\r\n]", " ", line))
            continue
        chars = list(line)
        i = 0
        while i < len(line):
            if line[i] != "\u0060" or (i > 0 and line[i - 1] == "\\"):
                i += 1
                continue
            run_end = i + 1
            while run_end < len(line) and line[run_end] == "\u0060":
                run_end += 1
            run = line[i:run_end]
            close_at = line.find(run, run_end)
            if close_at < 0:
                i = run_end
                continue
            for pos in range(i, close_at + len(run)):
                if chars[pos] not in "\r\n":
                    chars[pos] = " "
            i = close_at + len(run)
        output.append("".join(chars))
    return "".join(output)


def _answer_citation_indices(answer):
    """Return citation indices in visible prose only."""
    visible_answer = _mask_markdown_code(answer)
    return sorted({int(value) for value in re.findall(r"\[(\d+)\]", visible_answer)})


def result_from_response(question, response):
    answer = response.get("answer")
    answer = answer if isinstance(answer, str) and answer.strip() else None
    sources = response.get("sources") if isinstance(response.get("sources"), list) else []
    indices = _answer_citation_indices(answer)
    invalid = {index for index in indices if index < 1 or index > len(sources)}
    retrieved_source_ids = []
    for hit in sources:
        if not isinstance(hit, dict):
            continue
        source_id = hit.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            continue
        source_id = source_id.strip()
        if source_id not in retrieved_source_ids:
            retrieved_source_ids.append(source_id)

    cited_sources = []
    cited_pins = []
    citations = []
    used_unverified_source = False
    for index in indices:
        if index < 1 or index > len(sources):
            continue
        hit = sources[index - 1]
        if not isinstance(hit, dict):
            invalid.add(index)
            continue
        source_id = hit.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            invalid.add(index)
            continue
        source_id = source_id.strip()
        if source_id not in cited_sources:
            cited_sources.append(source_id)
        citation = {"source_id": source_id}
        pin = _pin_cite(hit)
        if pin:
            citation["pin_cite"] = pin
            item = {"source_id": source_id, "pin_cite": pin}
            if item not in cited_pins:
                cited_pins.append(item)
        if citation not in citations:
            citations.append(citation)
        # Only the explicit, current verified-corpus status counts as verified.
        # Missing/unknown status is conservatively treated as unverified.
        if hit.get("source_status") != "verified_operative_text":
            used_unverified_source = True

    requested_as_of = question.get("as_of_date")
    return {
        "id": question["id"],
        "question_id": question["id"],
        "answer": answer,
        "abstained": bool(response.get("abstained", answer is None)),
        "retrieved_source_ids": retrieved_source_ids,
        "citations": citations,
        "used_unverified_source": used_unverified_source,
        "citation_marker_count": len(indices),
        "cited_sources": cited_sources,
        "cited_pin_cites": cited_pins,
        "invalid_citation_indices": sorted(invalid),
        "found": bool(response.get("found")),
        "scope": response.get("scope", "verified_corpus"),
        "requested_as_of": response.get("requested_as_of") or requested_as_of,
        "source_summary": [
            {
                "source_id": hit.get("source_id"),
                "citation": hit.get("citation") or hit.get("ref"),
                "article": hit.get("article"),
                "page": hit.get("page"),
                "source_status": hit.get("source_status"),
            }
            for hit in sources if isinstance(hit, dict)
        ],
    }

def _request_json(opener, url, payload, headers=None, timeout=180):
    request_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        request_headers.update(headers)
    request = urllib.request.Request(
        url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=request_headers, method="POST",
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            raw = response.read(MAX_API_RESPONSE_BYTES + 1)
            if not isinstance(raw, bytes) or len(raw) > MAX_API_RESPONSE_BYTES:
                raise RunnerError("API response exceeded the 16 MiB safety limit")
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not print response bodies: they can contain legal questions or user details.
        raise RunnerError(f"API request failed with HTTP {exc.code} at {url.rsplit('/', 1)[-1]}") from exc
    except urllib.error.URLError as exc:
        raise RunnerError(f"API request could not reach {url.rsplit('/', 1)[-1]}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RunnerError("API returned a non-JSON response") from exc


def run_questions(base_url, email, password, questions, out_path, sleep_seconds=3.1, allow_remote=False):
    base_url = validate_base_url(base_url, allow_remote=allow_remote)
    target = Path(out_path)
    if target.exists():
        raise RunnerError(f"output already exists: {target}; choose a new path to avoid overwriting results")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    base = base_url.rstrip("/")
    _request_json(opener, base + "/login", {"email": email, "password": password}, timeout=30)
    csrf = next((cookie.value for cookie in jar if cookie.name == "lc_csrf"), None)
    if not csrf:
        raise RunnerError("login succeeded without a CSRF cookie; cannot safely post questions")
    headers = {"X-CSRF-Token": csrf}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        for index, question in enumerate(questions):
            payload = {
                "q": question["question_ar"],
                "case_id": None,
                "as_of": question.get("as_of_date"),
                "scope": "verified_corpus",
            }
            response = _request_json(opener, base + "/ask", payload, headers=headers)
            result = result_from_response(question, response)
            stream.write(json.dumps(result, ensure_ascii=False) + "\n")
            stream.flush()
            print(f"Completed {index + 1}/{len(questions)}: {question['id']}", file=sys.stderr)
            if index + 1 < len(questions) and sleep_seconds:
                time.sleep(sleep_seconds)
    return len(questions)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", required=True, help="Question JSONL; draft rows may be run but cannot be scored")
    parser.add_argument("--out", required=True, help="New JSONL path; existing files are never overwritten")
    parser.add_argument("--limit", type=int, help="Run only the first N questions")
    parser.add_argument("--sleep-seconds", type=float, default=3.1, help="Delay between questions to respect /ask rate limits")
    parser.add_argument("--base-url", default=os.environ.get("LEGAL_EVAL_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--allow-remote", action="store_true", help="Explicitly allow a remote API; HTTPS is required")
    parser.add_argument("--email", default=os.environ.get("LEGAL_EVAL_EMAIL"))
    parser.add_argument("--password", default=os.environ.get("LEGAL_EVAL_PASSWORD"))
    args = parser.parse_args(argv)
    if not args.email or not args.password:
        print("evaluation run refused: set LEGAL_EVAL_EMAIL and LEGAL_EVAL_PASSWORD", file=sys.stderr)
        return 2
    if args.sleep_seconds < 0:
        print("evaluation run refused: --sleep-seconds cannot be negative", file=sys.stderr)
        return 2
    try:
        questions = read_questions(args.questions, args.limit)
        count = run_questions(args.base_url, args.email, args.password, questions, args.out, args.sleep_seconds, allow_remote=args.allow_remote)
    except (OSError, RunnerError) as exc:
        print(f"evaluation run failed: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote {count} result rows to {args.out}. No accuracy score was calculated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
