#!/usr/bin/env python3
"""Score top-3 article retrieval, wrong-article answers, and abstention on reviewed labels only."""
import argparse
import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

REVIEWED = {"lawyer_reviewed", "approved_for_evaluation"}


def load_jsonl(path):
    rows = []
    for line_no, raw in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_no}: each row must be an object")
        rows.append(row)
    return rows


def _valid_reviewed(row):
    if row.get("review_status") not in REVIEWED:
        return False
    if not isinstance(row.get("answerable"), bool):
        raise ValueError(f"{row.get('id')}: reviewed question needs answerable=true/false")
    if not isinstance(row.get("reviewer_name"), str) or not row["reviewer_name"].strip():
        raise ValueError(f"{row.get('id')}: reviewer_name is required")
    if not isinstance(row.get("review_date"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["review_date"]):
        raise ValueError(f"{row.get('id')}: review_date must be YYYY-MM-DD")
    if date.fromisoformat(row["review_date"]).isoformat() != row["review_date"] or date.fromisoformat(row["review_date"]) > date.today():
        raise ValueError(f"{row.get('id')}: invalid or future review_date")
    url = row.get("review_evidence_url")
    try:
        parsed = urlsplit(url or "")
        _ = parsed.port
    except ValueError:
        parsed = None
    if (parsed is None or parsed.scheme != "https" or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.query or parsed.fragment):
        raise ValueError(f"{row.get('id')}: review_evidence_url must be clean HTTPS")
    expected = row.get("expected_article")
    if row["answerable"] and (not isinstance(expected, str) or not expected.strip()):
        raise ValueError(f"{row.get('id')}: answerable reviewed question needs expected_article")
    if not row["answerable"] and expected not in (None, ""):
        raise ValueError(f"{row.get('id')}: unanswerable question must not have an expected_article")
    if not row["answerable"] and row.get("must_abstain_if_unverified") is not True:
        raise ValueError(f"{row.get('id')}: unanswerable question must require abstention")
    return True


def score(questions, runs):
    q_by_id = {}
    for q in questions:
        qid = q.get("id")
        if not isinstance(qid, str) or not qid.strip() or qid in q_by_id:
            raise ValueError("question IDs must be unique non-empty strings")
        q_by_id[qid] = q
    r_by_id = {}
    for r in runs:
        qid = r.get("question_id")
        if not isinstance(qid, str) or not qid.strip() or qid in r_by_id:
            raise ValueError("run question_id values must be unique non-empty strings")
        if qid not in q_by_id:
            raise ValueError(f"run contains unknown question_id {qid}")
        if not isinstance(r.get("abstained"), bool):
            raise ValueError(f"{qid}: abstained must be boolean")
        for field in ("retrieved_article_ids", "cited_article_ids"):
            value = r.get(field, [])
            if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
                raise ValueError(f"{qid}: {field} must be a list of non-empty article IDs")
            if len(value) != len(set(value)):
                raise ValueError(f"{qid}: {field} contains duplicates")
        r_by_id[qid] = r

    reviewed = [q for q in questions if _valid_reviewed(q)]
    excluded = len(questions) - len(reviewed)
    missing = sorted(q["id"] for q in reviewed if q["id"] not in r_by_id)
    if missing:
        raise ValueError("missing run records for reviewed questions: " + ", ".join(missing))
    extra = sorted(set(r_by_id) - {q["id"] for q in reviewed})
    if extra:
        raise ValueError("run records supplied for unreviewed questions: " + ", ".join(extra))

    answerable = [q for q in reviewed if q["answerable"]]
    top3_hits = []
    colloquial_synonym_hits = []
    wrong_answers = cited_non_abstained = non_abstained = abstained = 0
    uncited_non_abstained = 0
    unanswerable = unanswerable_abstained = 0
    for q in reviewed:
        run = r_by_id[q["id"]]
        abstained += int(run["abstained"])
        if q["answerable"]:
            expected = q["expected_article"].strip()
            hit = int(expected in run["retrieved_article_ids"][:3])
            top3_hits.append(hit)
            tags = q.get("retrieval_tags", [])
            if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                raise ValueError(f'{q["id"]}: retrieval_tags must be a list of strings')
            if q.get("question_style") == "colloquial" or "synonym" in tags:
                colloquial_synonym_hits.append(hit)
        else:
            unanswerable += 1
            unanswerable_abstained += int(run["abstained"])
        if not run["abstained"]:
            non_abstained += 1
            cited = run["cited_article_ids"]
            if not cited:
                uncited_non_abstained += 1
            else:
                cited_non_abstained += 1
                expected = q.get("expected_article")
                if (not q["answerable"]) or any(x != expected for x in cited):
                    wrong_answers += 1

    return {
        "reviewed_questions": len(reviewed),
        "answerable_questions": len(answerable),
        "unanswerable_questions": unanswerable,
        "unlabeled_or_unreviewed_excluded": excluded,
        "top3_hit_rate": round(sum(top3_hits) / len(top3_hits), 4) if top3_hits else None,
        "top3_hit_rate_colloquial_or_synonym": round(sum(colloquial_synonym_hits) / len(colloquial_synonym_hits), 4) if colloquial_synonym_hits else None,
        "colloquial_or_synonym_questions": len(colloquial_synonym_hits),
        "wrong_article_rate": round(wrong_answers / cited_non_abstained, 4) if cited_non_abstained else None,
        "wrong_article_answers": wrong_answers,
        "cited_non_abstained_answers": cited_non_abstained,
        "non_abstained_answers": non_abstained,
        "uncited_non_abstained_answers": uncited_non_abstained,
        "abstention_rate": round(abstained / len(reviewed), 4) if reviewed else None,
        "abstention_compliance_unanswerable": round(unanswerable_abstained / unanswerable, 4) if unanswerable else None,
        "abstained_answers": abstained,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    parser.add_argument("--min-score", type=float, default=0.3)
    parser.add_argument("--output", default="docs/arabic_retrieval_measurement.json")
    args = parser.parse_args()
    if not math.isfinite(args.min_score) or not 0 <= args.min_score <= 1:
        parser.error("--min-score must be a finite value from 0 to 1")
    questions = load_jsonl(args.questions)
    runs = load_jsonl(args.runs)
    metrics = score(questions, runs)
    raw = Path(args.questions).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    report_path = Path(args.output)
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    else:
        report = {"schema_version": 1, "benchmark_sha256": digest, "phases": {"before": None, "after": None}}
    if report.get("benchmark_sha256") is None:
        report["benchmark_sha256"] = digest
    if report.get("benchmark_sha256") != digest:
        raise SystemExit("benchmark hash changed; start a new comparison report instead of mixing question sets")
    report["phases"][args.phase] = {
        "min_score": args.min_score,
        "metrics": metrics,
        "status": "scored" if metrics["reviewed_questions"] else "not_scored_no_lawyer_approved_labels",
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
