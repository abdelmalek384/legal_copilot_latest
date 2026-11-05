#!/usr/bin/env python3
"""Build a disposable fictional firm and measure the main read paths at scale.

Run from the repository root:
    PYTHONPATH=. python tools/scale_smoke.py

All databases and original files are created under a temporary directory. The
script uses DatabaseRuntime provisioning/identity methods and the same
authenticated HTTP routes used by the application; it never seeds tenant rows
with ad-hoc SQL.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path

from docx import Document
from fastapi.testclient import TestClient


PASSWORD = "ScaleSmoke-Fictional-Only-2026!"
OWNER_EMAIL = "scale-owner@example.test"
DOCX_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
ENV_NAMES = (
    "COPILOT_DB",
    "COPILOT_CONTROL_DB",
    "COPILOT_TENANT_DB_ROOT",
    "COPILOT_CORPUS_DB",
    "COPILOT_OBJECT_STORAGE_ROOT",
    "COPILOT_OBJECT_STORAGE_BACKEND",
    "COPILOT_ENV",
    "COPILOT_ALLOWED_HOSTS",
    "COPILOT_SECURE_COOKIES",
    "ADMIN_TOKEN",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=int, default=2000)
    parser.add_argument("--users", type=int, default=50)
    parser.add_argument("--passages", type=int, default=20000)
    parser.add_argument("--invoices", type=int, default=5000)
    parser.add_argument("--samples", type=int, default=10)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--keep-data", action="store_true")
    args = parser.parse_args()
    for name in ("cases", "users", "passages", "invoices", "samples"):
        if getattr(args, name) < 1:
            parser.error(f"--{name} must be at least 1")
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")
    return args


def set_disposable_environment(root: Path) -> dict[str, str | None]:
    previous = {name: os.environ.get(name) for name in ENV_NAMES}
    os.environ.pop("COPILOT_DB", None)
    os.environ.update(
        {
            "COPILOT_CONTROL_DB": str(root / "control.sqlite3"),
            "COPILOT_TENANT_DB_ROOT": str(root / "tenants"),
            "COPILOT_CORPUS_DB": str(root / "corpus.sqlite3"),
            "COPILOT_OBJECT_STORAGE_ROOT": str(root / "objects"),
            "COPILOT_OBJECT_STORAGE_BACKEND": "local",
            "COPILOT_ENV": "development",
            "COPILOT_ALLOWED_HOSTS": "testserver,localhost,127.0.0.1",
            "COPILOT_SECURE_COOKIES": "0",
            "ADMIN_TOKEN": "scale-smoke-admin-token-for-disposable-fixture",
        }
    )
    return previous


def restore_environment(previous: dict[str, str | None]) -> None:
    for name, value in previous.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value


def request(client: TestClient, method: str, path: str, **kwargs):
    headers = dict(kwargs.pop("headers", {}) or {})
    if method.lower() not in {"get", "head", "options"}:
        headers["X-CSRF-Token"] = client.cookies.get("lc_csrf", "")
    response = getattr(client, method.lower())(path, headers=headers, **kwargs)
    if response.status_code != 200:
        detail = response.text[:1000]
        raise RuntimeError(
            f"{method.upper()} {path} returned {response.status_code}: {detail}"
        )
    return response


def seed_users(runtime, app_module, firm_id: int, count: int) -> int:
    password_hash = app_module.hash_pw(PASSWORD)
    owner_id = runtime.create_initial_firm_owner(
        firm_id, "Scale Smoke Owner", OWNER_EMAIL, password_hash
    )
    for number in range(2, count + 1):
        user_id = runtime.create_global_identity(
            f"Scale Smoke User {number:03d}",
            f"scale-user-{number:03d}@example.test",
            password_hash,
        )
        runtime.create_firm_membership(
            user_id, firm_id, "lawyer" if number % 2 else "junior",
            created_by_user_id=owner_id,
        )
    return owner_id


def seed_cases(client: TestClient, case_count: int) -> list[dict]:
    created = 0
    for start in range(1, case_count + 1, 500):
        stop = min(case_count, start + 499)
        output = io.StringIO(newline="")
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(("title", "client", "stage", "case_number", "case_year"))
        for number in range(start, stop + 1):
            writer.writerow(
                (
                    f"Synthetic scale matter {number:05d}",
                    f"Scale Client {number:05d}",
                    "benchmark",
                    f"SM-{number:05d}",
                    "2026",
                )
            )
        response = request(
            client, "post", "/cases/import.csv",
            json={"csv": output.getvalue()},
        )
        result = response.json()
        expected = stop - start + 1
        if int(result.get("created", 0)) != expected:
            raise RuntimeError(
                f"case import created {result.get('created')} of {expected} requested rows"
            )
        created += expected
    cases = request(client, "get", "/cases").json()
    if created != case_count or len(cases) != case_count:
        raise RuntimeError(
            f"expected {case_count} cases; imported {created} and listed {len(cases)}"
        )
    return cases


def docx_passages(first_index: int, count: int) -> bytes:
    """Create one bounded DOCX whose paragraphs become individual FTS passages."""
    document = Document()
    for index in range(first_index, first_index + count):
        prefix = f"scale passage {index:05d} synthetic searchable legal evidence "
        padding = "fictional benchmark material and searchable passage " * 80
        text = (prefix + padding)[:1536]
        if len(text) < 1536:
            text += "x" * (1536 - len(text))
        document.add_paragraph(text)
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def seed_passages(
    client: TestClient, case_id: int, passage_count: int
) -> int:
    total = 0
    document_number = 0
    next_passage = 1
    while total < passage_count:
        count = min(650, passage_count - total)
        payload = docx_passages(next_passage, count)
        response = request(
            client, "post", f"/cases/{case_id}/upload",
            files={
                "file": (
                    f"scale-passages-{document_number + 1:03d}.docx",
                    payload,
                    DOCX_CONTENT_TYPE,
                )
            },
        )
        inserted = int(response.json().get("chunks", 0))
        if inserted != count:
            raise RuntimeError(
                f"document upload created {inserted} passages; expected {count}"
            )
        total += inserted
        next_passage += count
        document_number += 1
        print(f"  passages: {total:,}/{passage_count:,}", flush=True)
    return total


def seed_invoices(client: TestClient, case_id: int, invoice_count: int) -> int:
    payload = {
        "description": "Synthetic scale-smoke legal services",
        "due_date": "2099-12-31",
        "lines": [
            {
                "description": "Synthetic benchmark line",
                "quantity_milli": 1000,
                "unit_price_piasters": 1000,
            }
        ],
    }
    for number in range(1, invoice_count + 1):
        draft = request(
            client, "post", f"/cases/{case_id}/invoices", json=payload
        ).json()
        request(client, "post", f"/invoices/{int(draft['id'])}/issue")
        if number % 250 == 0 or number == invoice_count:
            print(f"  invoices: {number:,}/{invoice_count:,}", flush=True)
    listed = request(client, "get", "/invoices").json().get("invoices", [])
    if len(listed) != invoice_count:
        raise RuntimeError(
            f"expected {invoice_count} invoices; list returned {len(listed)}"
        )
    return len(listed)


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def measure(
    client: TestClient,
    name: str,
    method: str,
    path: str,
    *,
    samples: int,
    warmups: int,
    target_ms: float | None,
    json_body: dict | None = None,
) -> dict:
    def call():
        kwargs = {"json": json_body} if json_body is not None else {}
        return request(client, method, path, **kwargs)

    for _ in range(warmups):
        call()
    timings = []
    for _ in range(samples):
        started = time.perf_counter()
        call()
        timings.append((time.perf_counter() - started) * 1000)
    p50 = statistics.median(timings)
    p95 = percentile(timings, 0.95)
    return {
        "name": name,
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "target_ms": target_ms,
        "passed": target_ms is None or p95 < target_ms,
    }


def run(args: argparse.Namespace) -> int:
    if args.keep_data:
        root = Path(tempfile.mkdtemp(prefix="legal-copilot-scale-"))
        temporary = None
    else:
        temporary = tempfile.TemporaryDirectory(prefix="legal-copilot-scale-")
        root = Path(temporary.name)

    previous_env = set_disposable_environment(root)
    runtime = None
    client = None
    app_module = None
    try:
        # Import only after forcing disposable development database paths.
        import app as app_module
        from database_runtime import DatabaseRuntime

        app_module._database_runtime = None
        runtime = DatabaseRuntime.from_env()
        runtime.initialize()
        firm_id, _ = runtime.provision_firm("Synthetic Scale Smoke Firm")
        owner_id = seed_users(runtime, app_module, firm_id, args.users)
        app_module._database_runtime = runtime
        # The real upload quota is an abuse-control policy, not a benchmark
        # target. Raise it only inside this disposable process so the full
        # 20,000-passage fixture can still use the authenticated upload route.
        required_uploads = math.ceil(args.passages / 650)
        app_module._UPLOAD_RATE_LIMIT = (max(10, required_uploads), 3600)
        app_module._RATE_LIMITS = dict(app_module._RATE_LIMITS)
        app_module._RATE_LIMITS["/firm/data-export.zip"] = (
            max(2, args.samples + args.warmups), 3600
        )

        client = TestClient(app_module.app)
        login = client.post(
            "/login", json={"email": OWNER_EMAIL, "password": PASSWORD}
        )
        if login.status_code != 200:
            raise RuntimeError(f"scale owner login failed: {login.status_code} {login.text[:500]}")
        if not client.cookies.get("lc_csrf"):
            raise RuntimeError("login did not issue the expected CSRF cookie")

        print(f"Seeding {args.cases:,} cases and {args.users:,} users...", flush=True)
        cases = seed_cases(client, args.cases)
        case_id = int(cases[0]["id"])

        print(f"Seeding {args.passages:,} searchable passages...", flush=True)
        passages = seed_passages(client, case_id, args.passages)

        print(f"Seeding {args.invoices:,} issued invoices...", flush=True)
        invoices = seed_invoices(client, case_id, args.invoices)

        search_response = request(
            client, "post", "/search",
            json={
                "q": "scale passage synthetic searchable evidence",
                "case_id": case_id,
                "scope": "firm_documents",
            },
        )
        if not search_response.json():
            raise RuntimeError("scale search fixture returned no searchable passages")

        tenant = runtime.firm_connection(runtime.resolve_context(owner_id, firm_id))
        plan = tenant.execute(
            "EXPLAIN QUERY PLAN SELECT i.* FROM invoices i "
            "WHERE i.case_id IN (SELECT id FROM cases WHERE firm_id=?) "
            "ORDER BY i.created_at DESC,i.id DESC",
            (firm_id,),
        ).fetchall()
        print(
            "Invoice list query plan: "
            + " | ".join(str(row["detail"]) for row in plan),
            flush=True,
        )

        checks = [
            ("dashboard", "get", "/dashboard", 300.0, None),
            ("case_list", "get", "/cases", 300.0, None),
            ("case_detail", "get", f"/cases/{case_id}", None, None),
            (
                "search", "post", "/search", 500.0,
                {
                    "q": "scale passage synthetic searchable evidence",
                    "case_id": case_id,
                    "scope": "firm_documents",
                },
            ),
            ("invoice_list", "get", "/invoices", 300.0, None),
            ("finance_overview", "get", "/finance/overview", 300.0, None),
            (
                "invoice_finance_overview", "get", "/finance/invoices/overview",
                300.0, None,
            ),
            ("firm_export", "get", "/firm/data-export.zip", None, None),
        ]
        results = []
        invoice_record_build_ms = []
        original_invoice_records = app_module._invoice_records

        def profile_invoice_records(connection, rows):
            started = time.perf_counter()
            try:
                return original_invoice_records(connection, rows)
            finally:
                invoice_record_build_ms.append((time.perf_counter() - started) * 1000)

        app_module._invoice_records = profile_invoice_records
        print("Measuring authenticated read paths...", flush=True)
        try:
            for name, method, path, target, body in checks:
                results.append(
                    measure(
                        client, name, method, path, samples=args.samples,
                        warmups=args.warmups, target_ms=target, json_body=body,
                    )
                )
        finally:
            app_module._invoice_records = original_invoice_records

        if invoice_record_build_ms:
            print(
                "Invoice child-record builder p50/p95 ms: "
                f"{statistics.median(invoice_record_build_ms):.2f}/"
                f"{percentile(invoice_record_build_ms, 0.95):.2f}",
                flush=True,
            )

        print("\nSeeded fixture:")
        print(
            f"  firm_id={firm_id}; users={args.users:,}; cases={len(cases):,}; "
            f"passages={passages:,}; invoices={invoices:,}"
        )
        print("\nEndpoint                 p50 ms    p95 ms    target    result")
        print("-" * 66)
        for item in results:
            target = (
                "—" if item["target_ms"] is None
                else f"<{item['target_ms']:.0f} ms"
            )
            status = "MEASURED" if item["target_ms"] is None else (
                "PASS" if item["passed"] else "MISS"
            )
            print(
                f"{item['name']:<24} {item['p50_ms']:>7.2f} "
                f"{item['p95_ms']:>9.2f} {target:>9} {status:>9}"
            )
        print("\nJSON:")
        print(json.dumps(results, ensure_ascii=False, indent=2))
        misses = [item for item in results if not item["passed"]]
        if misses:
            print(
                "\nPerformance targets missed: "
                + ", ".join(item["name"] for item in misses),
                file=sys.stderr,
            )
            return 1
        return 0
    finally:
        if client is not None:
            client.close()
        if runtime is not None:
            try:
                runtime.close_current_thread()
            except Exception:
                pass
        if app_module is not None:
            app_module._database_runtime = None
        restore_environment(previous_env)
        if temporary is not None:
            temporary.cleanup()
        elif args.keep_data:
            print(f"Disposable scale-smoke data retained at: {root}", flush=True)


if __name__ == "__main__":
    raise SystemExit(run(parse_args()))
