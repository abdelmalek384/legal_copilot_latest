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


def validate_base_url(base_url, allow_remote=False):
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise RunnerError("base URL must be an HTTP(S) origin without embedded credentials")
    if parsed.query or parsed.fragment:
        raise RunnerError("base URL must not contain a query string or fragment")
    host = parsed.hostname.lower()
    loopback = host in {"localhost", "127.0.0.1", "::1"}
    if not loopback and not allow_remote:
        raise RunnerError("non-local API targets require the explicit --allow-remote flag")
    if not loopback and parsed.scheme != "https":
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


def result_from_response(question, response):
    answer = response.get("answer")
    answer = answer if isinstance(answer, str) and answer.strip() else None
    sources = response.get("sources") if isinstance(response.get("sources"), list) else []
    indices = sorted({int(x) for x in re.findall(r"\[(\d+)\]", answer or "")})
    invalid = [index for index in indices if index < 1 or index > len(sources)]
    valid_indices = [index for index in indices if 1 <= index <= len(sources)]
    cited_sources = []
    cited_pins = []
    for index in valid_indices:
        hit = sources[index - 1]
        if not isinstance(hit, dict):
            continue
        source_id = hit.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            continue
        source_id = source_id.strip()
        if source_id not in cited_sources:
            cited_sources.append(source_id)
        pin = _pin_cite(hit)
        if pin:
            item = {"source_id": source_id, "pin_cite": pin}
            if item not in cited_pins:
                cited_pins.append(item)
    requested_as_of = question.get("as_of_date")
    return {
        "id": question["id"],
        "answer": answer,
        "abstained": bool(response.get("abstained", answer is None)),
        "cited_sources": cited_sources,
        "cited_pin_cites": cited_pins,
        "invalid_citation_indices": invalid,
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
            return json.loads(response.read().decode("utf-8"))
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
