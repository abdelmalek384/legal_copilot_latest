#!/usr/bin/env python3
"""Score top-3 article retrieval, wrong-article answers, and abstention on reviewed labels only."""
import argparse
import hashlib
import json
import math
import re
import os
import stat
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

try:
    from tools.evaluate_legal_answer_reviews import validate_reviewer_registry
except ModuleNotFoundError:  # supports direct execution as python tools/score_arabic_retrieval.py
    from evaluate_legal_answer_reviews import validate_reviewer_registry

REVIEWED = {"lawyer_reviewed", "approved_for_evaluation"}
MIN_TARGET_COHORT_SIZE = 20
MIN_TOTAL_REVIEWED_QUESTIONS = 100


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object repeats a key at any nesting depth."""


def _reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _is_one_of(value, choices):
    """Return false for malformed, unhashable JSON enum values."""
    return isinstance(value, str) and value in choices


def _is_canonical_article_id(value):
    """Validate the non-empty source/law/article components of a canonical ID."""
    if (not isinstance(value, str) or value != value.strip()
            or any(ord(char) < 32 or ord(char) == 127 for char in value)
            or value.count("::law:") != 1 or value.count("::article:") != 1):
        return False
    source_id, _, remainder = value.partition("::law:")
    law_label, _, article_label = remainder.rpartition("::article:")
    return bool(
        source_id and source_id == source_id.strip()
        and law_label and law_label == law_label.strip()
        and article_label and article_label == article_label.strip()
    )


def read_regular_file(path, *, max_bytes=64 * 1024 * 1024):
    """Read a bounded scorer input from one stable regular-file descriptor."""
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"{path}: input must be a regular file")
    if before.st_size > max_bytes:
        raise ValueError(f"{path}: input exceeds the {max_bytes}-byte size limit")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError(f"{path}: input changed while opening")
        data = stream.read(max_bytes + 1)
        after = os.fstat(stream.fileno())
        current = path.lstat()
        if len(data) > max_bytes or len(data) != after.st_size:
            raise ValueError(f"{path}: input changed size or exceeds limit")
        if (
            (opened.st_dev, opened.st_ino) != (after.st_dev, after.st_ino)
            or (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns)
            != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)
            or (current.st_dev, current.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise ValueError(f"{path}: input changed while being read")
    return data


def load_jsonl(path):
    rows = []
    for line_no, raw in enumerate(read_regular_file(path).decode("utf-8-sig").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        try:
            row = json.loads(raw, object_pairs_hook=_reject_duplicate_json_keys)
        except DuplicateJSONKeyError as exc:
            raise ValueError(f"{path}:{line_no}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: each row must be an object")
        rows.append(row)
    return rows


def _valid_reviewed(row, approved_reviewers):
    if not _is_one_of(row.get("review_status"), REVIEWED):
        return False
    if not _is_one_of(row.get("question_origin"), {"observed_anonymized_query", "permitted_public_q_and_a"}):
        raise ValueError(f'{row.get("id")}: only provenance-cleared observed questions may be scored')
    if row.get("privacy_review_status") != "approved":
        raise ValueError(f'{row.get("id")}: privacy_review_status must be approved')
    collection_date = row.get("question_collection_date")
    if (not isinstance(collection_date, str)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", collection_date)):
        raise ValueError(f'{row.get("id")}: question_collection_date must be YYYY-MM-DD')
    try:
        parsed_collection_date = date.fromisoformat(collection_date)
    except ValueError:
        parsed_collection_date = None
    if parsed_collection_date is None or parsed_collection_date.isoformat() != collection_date or parsed_collection_date > date.today():
        raise ValueError(f'{row.get("id")}: invalid or future question_collection_date')
    for field in ("question_origin_reference", "consent_or_reuse_basis"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f'{row.get("id")}: {field} is required')
    if not _is_one_of(row.get("label_status"), {"lawyer_approved", "approved_for_evaluation"}):
        raise ValueError(f'{row.get("id")}: reviewed question must have an approved label_status')
    if not isinstance(row.get("answerable"), bool):
        raise ValueError(f"{row.get('id')}: reviewed question needs answerable=true/false")
    if not isinstance(row.get("reviewer_id"), str) or not row["reviewer_id"].strip():
        raise ValueError(f"{row.get('id')}: reviewer_id is required")
    if not isinstance(row.get("reviewer_name"), str) or not row["reviewer_name"].strip():
        raise ValueError(f"{row.get('id')}: reviewer_name is required")
    if not _is_one_of(row.get("reviewer_role"), {"egyptian_lawyer", "qualified_egyptian_counsel"}):
        raise ValueError(f"{row.get('id')}: reviewer_role must identify qualified Egyptian counsel")
    reviewer = approved_reviewers.get(row["reviewer_id"])
    if reviewer is None:
        raise ValueError(f"{row.get('id')}: reviewer_id must match a valid approved reviewer registry entry")
    if row["reviewer_name"] != reviewer.get("display_name"):
        raise ValueError(f"{row.get('id')}: reviewer_name must match the approved reviewer registry display_name")
    if row.get("practice_area", "unspecified") not in reviewer.get("practice_areas", []):
        raise ValueError(f"{row.get('id')}: reviewer is not approved for this practice_area")
    if row.get("reviewer_role") != reviewer.get("professional_role"):
        raise ValueError(f"{row.get('id')}: reviewer_role must match the approved reviewer registry professional_role")
    if not isinstance(row.get("lawyer_approved_answer"), str) or not row["lawyer_approved_answer"].strip():
        raise ValueError(f"{row.get('id')}: lawyer_approved_answer is required")
    if not isinstance(row.get("review_date"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["review_date"]):
        raise ValueError(f"{row.get('id')}: review_date must be YYYY-MM-DD")
    if date.fromisoformat(row["review_date"]).isoformat() != row["review_date"] or date.fromisoformat(row["review_date"]) > date.today():
        raise ValueError(f"{row.get('id')}: invalid or future review_date")
    url = row.get("review_evidence_url")
    parsed = None
    if (isinstance(url, str) and url and url == url.strip()
            and not any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in url)
            and "?" not in url and "#" not in url and "\\" not in url):
        try:
            parsed = urlsplit(url)
            _ = parsed.port
        except (TypeError, ValueError):
            parsed = None
    if (parsed is None or parsed.scheme.lower() != "https" or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.netloc.endswith(":") or parsed.query or parsed.fragment):
        raise ValueError(f"{row.get('id')}: review_evidence_url must be clean HTTPS")
    expected = row.get("expected_article")
    expected_id = row.get("expected_article_id")
    if expected not in (None, "") and (not isinstance(expected, str) or expected != expected.strip()):
        raise ValueError(f"{row.get('id')}: expected_article must be a trimmed string")
    if expected_id not in (None, "") and not _is_canonical_article_id(expected_id):
        raise ValueError(f'{row.get("id")}: expected_article_id must use non-empty source_id::law:<law-label>::article:<article> components')
    if row["answerable"]:
        if not isinstance(expected, str) or not expected.strip():
            raise ValueError(f"{row.get('id')}: answerable reviewed question needs a human-readable expected_article")
        if not isinstance(expected_id, str) or not expected_id.strip():
            raise ValueError(f"{row.get('id')}: answerable reviewed question needs canonical expected_article_id")

    if not row["answerable"] and (expected not in (None, "") or expected_id not in (None, "")):
        raise ValueError(f"{row.get('id')}: unanswerable question must not have an expected article")
    if not row["answerable"] and row.get("must_abstain_if_unverified") is not True:
        raise ValueError(f"{row.get('id')}: unanswerable question must require abstention")
    return True


def benchmark_fingerprint(questions):
    """Hash immutable prompt identity/text, not counsel labels added after baseline capture."""
    stable = [
        {
            "id": q["id"],
            "practice_area": q.get("practice_area"),
            "question_ar": q.get("question_ar"),
            "question_origin": q.get("question_origin"),
            # Cohort-defining prompt metadata must stay fixed across before/after runs.
            "question_style": q.get("question_style"),
            "retrieval_tags": sorted(q.get("retrieval_tags", []))
            if isinstance(q.get("retrieval_tags", []), list)
            and all(isinstance(tag, str) for tag in q.get("retrieval_tags", []))
            else q.get("retrieval_tags"),
        }
        for q in questions
    ]
    stable.sort(key=lambda row: row["id"])
    payload = json.dumps(
        stable, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def score(questions, runs, reviewer_registry):
    q_by_id = {}
    for index, q in enumerate(questions, start=1):
        if not isinstance(q, dict):
            raise ValueError(f"question row {index} must be an object")
        qid = q.get("id")
        if not isinstance(qid, str) or not qid.strip() or qid != qid.strip() or qid in q_by_id:
            raise ValueError("question IDs must be unique non-empty strings")
        q_by_id[qid] = q
    r_by_id = {}
    for index, r in enumerate(runs, start=1):
        if not isinstance(r, dict):
            raise ValueError(f"run row {index} must be an object")
        qid = r.get("question_id")
        if not isinstance(qid, str) or not qid.strip() or qid != qid.strip() or qid in r_by_id:
            raise ValueError("run question_id values must be unique non-empty strings")
        if qid not in q_by_id:
            raise ValueError(f"run contains unknown question_id {qid}")
        if not isinstance(r.get("abstained"), bool):
            raise ValueError(f"{qid}: abstained must be boolean")
        if not isinstance(r.get("used_unverified_source"), bool):
            raise ValueError(f"{qid}: used_unverified_source must be boolean")
        for field in ("retrieved_article_ids", "cited_article_ids"):
            value = r.get(field, [])
            if not isinstance(value, list) or any(
                    not isinstance(x, str) or not x.strip() or x != x.strip()
                    for x in value):
                raise ValueError(f"{qid}: {field} must be a list of trimmed, non-empty article IDs")
            if len(value) != len(set(value)):
                raise ValueError(f"{qid}: {field} contains duplicates")
        if not set(r.get("cited_article_ids", [])).issubset(set(r.get("retrieved_article_ids", []))):
            raise ValueError(f"{qid}: cited_article_ids must be present in retrieved_article_ids")
        invalid_indices = r.get("invalid_citation_indices")
        marker_count = r.get("citation_marker_count")
        if invalid_indices is not None and (
                not isinstance(invalid_indices, list)
                or any(type(index) is not int or index < 1 for index in invalid_indices)
                or len(invalid_indices) != len(set(invalid_indices))):
            raise ValueError(f"{qid}: invalid_citation_indices must be a list of unique positive integers")
        if marker_count is not None and (type(marker_count) is not int or marker_count < 0):
            raise ValueError(f"{qid}: citation_marker_count must be a non-negative integer")
        if invalid_indices is not None and marker_count is not None and len(invalid_indices) > marker_count:
            raise ValueError(f"{qid}: invalid citation count cannot exceed citation_marker_count")
        r_by_id[qid] = r

    approved_reviewers, registry_errors = validate_reviewer_registry(reviewer_registry)
    if registry_errors:
        raise ValueError("reviewer registry contains invalid entries: " + "; ".join(
            f"{item.get('record')}: {', '.join(item.get('errors', []))}" for item in registry_errors
        ))
    if not approved_reviewers:
        raise ValueError("reviewer registry has no valid approved reviewers")
    reviewed = [q for q in questions if _valid_reviewed(q, approved_reviewers)]
    excluded = len(questions) - len(reviewed)
    missing = sorted(q["id"] for q in reviewed if q["id"] not in r_by_id)
    if missing:
        raise ValueError("missing run records for reviewed questions: " + ", ".join(missing))
    reviewed_ids = {q["id"] for q in reviewed}
    # Keep baseline run artifacts for known unlabeled questions, but exclude them
    # from every metric until counsel approves their labels.
    excluded_run_ids = set(r_by_id) - reviewed_ids

    answerable = [q for q in reviewed if q["answerable"]]
    top3_hits = []
    colloquial_hits = []
    synonym_hits = []
    colloquial_synonym_hits = []
    wrong_answers = cited_non_abstained = non_abstained = abstained = 0
    uncited_non_abstained = 0
    invalid_citation_markers = 0
    invalid_citation_answers = 0
    citation_validation_missing = 0
    unverified_source_answers = 0
    unanswerable = unanswerable_abstained = 0
    answerable_abstained = 0
    for q in reviewed:
        run = r_by_id[q["id"]]
        abstained += int(run["abstained"])
        invalid_indices = run.get("invalid_citation_indices")
        marker_count = run.get("citation_marker_count")
        if invalid_indices is None or marker_count is None:
            citation_validation_missing += 1
        if invalid_indices:
            invalid_citation_markers += len(invalid_indices)
            invalid_citation_answers += 1
        if q["answerable"]:
            expected = (q.get("expected_article_id") or q.get("expected_article") or "").strip()
            hit = int(expected in run["retrieved_article_ids"][:3])
            top3_hits.append(hit)
            answerable_abstained += int(run["abstained"])
            tags = q.get("retrieval_tags", [])
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                raise ValueError(f'{q["id"]}: retrieval_tags must be a list of strings')
            style_reviewed = q.get("question_style_review_status") == "lawyer_approved"
            tags_reviewed = q.get("retrieval_tags_review_status") == "lawyer_approved"
            is_colloquial = q.get("question_style") == "colloquial" and style_reviewed
            is_synonym = "synonym" in tags and tags_reviewed
            if is_colloquial:
                colloquial_hits.append(hit)
            if is_synonym:
                synonym_hits.append(hit)
            if is_colloquial or is_synonym:
                colloquial_synonym_hits.append(hit)
        else:
            unanswerable += 1
            unanswerable_abstained += int(run["abstained"])
        if not run["abstained"]:
            non_abstained += 1
            if run["used_unverified_source"]:
                unverified_source_answers += 1
            cited = run["cited_article_ids"]
            if not cited:
                uncited_non_abstained += 1
            else:
                cited_non_abstained += 1
                expected = q.get("expected_article_id") or q.get("expected_article")
                if (not q["answerable"]) or any(x != expected for x in cited):
                    wrong_answers += 1

    colloquial_rate = round(sum(colloquial_hits) / len(colloquial_hits), 4) if colloquial_hits else None
    synonym_rate = round(sum(synonym_hits) / len(synonym_hits), 4) if synonym_hits else None
    combined_rate = (
        round(sum(colloquial_synonym_hits) / len(colloquial_synonym_hits), 4)
        if colloquial_synonym_hits else None
    )
    wrong_rate = round(wrong_answers / cited_non_abstained, 4) if cited_non_abstained else None
    # A known safety failure must not be hidden behind an otherwise incomplete
    # evaluation cohort (for example, an unanswerable question answered without
    # a citation leaves wrong_rate=None but is still a definite abstention failure).
    known_safety_failure = (
        wrong_answers > 0
        or uncited_non_abstained > 0
        or unverified_source_answers > 0
        or invalid_citation_markers > 0
        or (unanswerable > 0 and unanswerable_abstained != unanswerable)
    )
    if known_safety_failure:
        target_status = "below_target"
    elif (len(reviewed) < MIN_TOTAL_REVIEWED_QUESTIONS or not top3_hits
            or len(colloquial_hits) < MIN_TARGET_COHORT_SIZE
            or len(synonym_hits) < MIN_TARGET_COHORT_SIZE or not unanswerable
            or colloquial_rate is None or synonym_rate is None or wrong_rate is None
            or citation_validation_missing > 0):
        target_status = "not_evaluable_missing_approved_labels_or_cited_runs"
    elif colloquial_rate < 0.80 or synonym_rate < 0.80 or wrong_rate != 0.0:
        target_status = "below_target"
    else:
        target_status = "targets_met"

    return {
        "reviewed_questions": len(reviewed),
        "answerable_questions": len(answerable),
        "answerable_abstained_answers": answerable_abstained,
        "answerable_non_abstained_answers": len(answerable) - answerable_abstained,
        "answerable_abstention_rate": round(answerable_abstained / len(answerable), 4) if answerable else None,
        "unanswerable_questions": unanswerable,
        "unlabeled_or_unreviewed_excluded": excluded,
        "unlabeled_run_records_excluded": len(excluded_run_ids),
        "top3_hit_rate": round(sum(top3_hits) / len(top3_hits), 4) if top3_hits else None,
        "top3_hit_rate_colloquial": colloquial_rate,
        "top3_hit_rate_synonym": synonym_rate,
        "top3_hit_rate_colloquial_or_synonym": combined_rate,
        "target_status": target_status,
        "target_top3_hit_rate_colloquial": 0.80,
        "target_top3_hit_rate_synonym": 0.80,
        "target_minimum_cohort_size": MIN_TARGET_COHORT_SIZE,
        "target_wrong_article_rate": 0.0,
        "target_uncited_non_abstained_answers": 0,
        "target_invalid_citation_markers": 0,
        "target_citation_validation_missing_runs": 0,
        "target_abstention_compliance_unanswerable": 1.0,
        "target_minimum_unanswerable_questions": 1,
        "target_minimum_reviewed_questions": MIN_TOTAL_REVIEWED_QUESTIONS,
        "colloquial_questions": len(colloquial_hits),
        "synonym_questions": len(synonym_hits),
        "colloquial_or_synonym_questions": len(colloquial_synonym_hits),
        "wrong_article_rate": wrong_rate,
        "wrong_article_answers": wrong_answers,
        "cited_non_abstained_answers": cited_non_abstained,
        "non_abstained_answers": non_abstained,
        "uncited_non_abstained_answers": uncited_non_abstained,
        "invalid_citation_answers": invalid_citation_answers,
        "invalid_citation_markers": invalid_citation_markers,
        "citation_validation_missing_runs": citation_validation_missing,
        "abstention_rate": round(abstained / len(reviewed), 4) if reviewed else None,
        "unverified_source_answers": unverified_source_answers,
        "unverified_source_rate": round(unverified_source_answers / non_abstained, 4) if non_abstained else None,
        "target_unverified_source_answers": 0,
        "abstention_compliance_unanswerable": round(unanswerable_abstained / unanswerable, 4) if unanswerable else None,
        "abstained_answers": abstained,
    }


def ensure_output_does_not_overwrite_inputs(output_path, input_paths):
    """Reject output paths that alias any source input, including symlinks/hardlinks."""
    output = Path(output_path)
    if output.is_symlink():
        raise ValueError("report output must not be a symlink")
    try:
        output_resolved = output.resolve()
        for input_path in input_paths:
            source = Path(input_path)
            if output_resolved == source.resolve():
                raise ValueError("report output must not overwrite question, run, or reviewer-registry inputs")
            if output.exists() and source.exists() and output.samefile(source):
                raise ValueError("report output must not overwrite question, run, or reviewer-registry inputs")
    except (OSError, RuntimeError) as exc:
        raise ValueError("unable to safely resolve report output and input paths") from exc


def write_report_atomically(report_path, content):
    """Replace a measurement report without exposing a partially written file."""
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=str(destination.parent)
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--reviewer-registry", required=True, help="private approved Egyptian-counsel registry JSON")
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    parser.add_argument("--min-score", type=float, default=0.3)
    parser.add_argument("--output", default="docs/arabic_retrieval_measurement.json")
    parser.add_argument("--replace-phase", action="store_true", help="explicitly replace an existing before/after phase in the report")
    args = parser.parse_args()
    if not math.isfinite(args.min_score) or not 0 <= args.min_score <= 1:
        parser.error("--min-score must be a finite value from 0 to 1")
    try:
        ensure_output_does_not_overwrite_inputs(
            args.output, (args.questions, args.runs, args.reviewer_registry)
        )
        questions = load_jsonl(args.questions)
        runs = load_jsonl(args.runs)
        reviewer_registry = json.loads(read_regular_file(args.reviewer_registry, max_bytes=2 * 1024 * 1024), object_pairs_hook=_reject_duplicate_json_keys)
        metrics = score(questions, runs, reviewer_registry)
        digest = benchmark_fingerprint(questions)
        report_path = Path(args.output)
        if report_path.exists():
            report = json.loads(read_regular_file(report_path, max_bytes=10 * 1024 * 1024), object_pairs_hook=_reject_duplicate_json_keys)
        else:
            report = {"schema_version": 1, "benchmark_sha256": digest, "phases": {"before": None, "after": None}}
        if not isinstance(report, dict) or not isinstance(report.get("phases"), dict):
            raise ValueError("measurement report must be a JSON object with a phases object")
        if report.get("benchmark_sha256") is None:
            report["benchmark_sha256"] = digest
        if report.get("benchmark_sha256") != digest:
            raise SystemExit("benchmark hash changed; start a new comparison report instead of mixing question sets")
        if args.phase in report["phases"] and report["phases"][args.phase] is not None and not args.replace_phase:
            raise ValueError(
                f"{args.phase} phase already exists; use --replace-phase only if intentionally replacing this measurement"
            )
        report["phases"][args.phase] = {
            "min_score": args.min_score,
            "metrics": metrics,
            "status": "scored" if metrics["reviewed_questions"] else "not_scored_no_lawyer_approved_labels",
        }
        write_report_atomically(
            report_path, json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
