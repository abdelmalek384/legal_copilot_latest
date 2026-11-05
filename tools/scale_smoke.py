#!/usr/bin/env python3
"""Seed and benchmark a fictional Legal Copilot firm at pilot-scale volumes.

Run with:
    COPILOT_ENV=development PYTHONPATH=. python tools/scale_smoke.py

The script creates isolated local SQLite databases and uses the application's
DatabaseRuntime and authenticated HTTP routes for all seeded application data.
It never connects to a configured production database or external provider.
"""
import argparse
import math
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path


CASE_COUNT = 2000
USER_COUNT = 50
PASSAGE_COUNT = 20000
INVOICE_COUNT = 5000
SYNTHETIC_PASSWORD = "Scale-Smoke-Fictional-2026!"
SYNTHETIC_QUERY = "scaleprobe"


def _percentile(samples, fraction):
    ordered = sorted(samples)
    if not ordered:
        return 0.0
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def _measure(client, method, path, *, samples=30, json_body=None):
    timings = []
    for _ in range(samples):
        started = time.perf_counter()
        headers = {"X-CSRF-Token": client.cookies.get("lc_csrf", "")}
        response = (
            getattr(client, method)(path, json=json_body, headers=headers)
            if json_body is not None
            else getattr(client, method)(path, headers=headers)
        )
        elapsed = (time.perf_counter() - started) * 1000
        if response.status_code != 200:
            raise RuntimeError(
                "{} {} returned {}: {}".format(method.upper(), path, response.status_code, response.text[:500])
            )
        timings.append(elapsed)
    return {
        "p50": statistics.median(timings),
        "p95": _percentile(timings, 0.95),
        "samples": len(timings),
    }


def _request(client, method, path, *, json_body=None):
    headers = {"X-CSRF-Token": client.cookies.get("lc_csrf", "")}
    response = getattr(client, method)(path, json=json_body, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(
            "{} {} returned {}: {}".format(method.upper(), path, response.status_code, response.text[:500])
        )
    return response.json()


def _prepare_environment(data_dir):
    if os.environ.get("COPILOT_ENV", "development").strip().lower() in {"prod", "production"}:
        raise RuntimeError("scale smoke must never run against production")
    data_dir.mkdir(parents=True, exist_ok=True)
    paths = (
        data_dir / "control.sqlite3",
        data_dir / "corpus.sqlite3",
        data_dir / "tenants",
        data_dir / "objects",
    )
    if any(path.exists() and (not path.is_dir() or any(path.iterdir())) for path in paths):
        raise RuntimeError("data directory must be empty; refusing to overwrite existing data")
    paths[2].mkdir(exist_ok=True)
    paths[3].mkdir(exist_ok=True)
    os.environ.update({
        "COPILOT_ENV": "development",
        "COPILOT_CONTROL_DB": str(paths[0]),
        "COPILOT_TENANT_DB_ROOT": str(paths[2]),
        "COPILOT_CORPUS_DB": str(paths[1]),
        "COPILOT_OBJECT_STORAGE_ROOT": str(paths[3]),
        "COPILOT_OBJECT_STORAGE_BACKEND": "local",
        "ADMIN_TOKEN": "scale-smoke-local-admin-token-2026",
    })


def _seed(runtime, client, firm_id, app_module):
    password_hash = app_module.hash_pw(SYNTHETIC_PASSWORD)
    for index in range(1, USER_COUNT):
        user_id = runtime.create_global_identity(
            "Scale Smoke Lawyer {:02d}".format(index),
            "scale-smoke-user-{:02d}@example.test".format(index),
            password_hash,
        )
        runtime.create_firm_membership(
            user_id, firm_id, "lawyer", created_by_user_id=None
        )
    print("Seeded {} firm users.".format(USER_COUNT), flush=True)

    case_ids = []
    for index in range(CASE_COUNT):
        payload = _request(
            client, "post", "/cases",
            json_body={
                "title": "Synthetic scale matter {:04d}".format(index + 1),
                "client": "",
                "case_number": "SMOKE-{:04d}".format(index + 1),
                "case_year": "2026",
            },
        )
        case_ids.append(int(payload["id"]))
        if (index + 1) % 250 == 0:
            print("Created {} / {} cases.".format(index + 1, CASE_COUNT), flush=True)
    print("Seeded {} cases.".format(len(case_ids)), flush=True)

    # Each 2,998-character paragraph becomes one passage: add_doc flushes
    # before combining it with the next paragraph. 100 paragraphs fit under
    # DocIn's 300,000-character limit; 200 documents therefore create exactly
    # 20,000 searchable passages without relying on implementation-specific
    # long-paragraph split boundaries.
    paragraph = "scaleprobe " + ("x" * 2987)
    passage_text = "\n\n".join([paragraph] * 100)
    if len(passage_text) > 300000:
        raise RuntimeError("synthetic passage document exceeds the API text limit")
    expected_chunks = 0
    for index in range(200):
        result = _request(
            client, "post", "/cases/{}/docs".format(case_ids[0]),
            json_body={
                "name": "Scale smoke passages {:03d}.txt".format(index + 1),
                "text": passage_text,
            },
        )
        chunks = int(result["chunks"])
        if chunks != 100:
            raise RuntimeError(
                "expected 100 passages per synthetic document, got {}".format(chunks)
            )
        expected_chunks += chunks
    print("Seeded {} searchable passages.".format(expected_chunks), flush=True)

    invoice_payload = {
        "description": "Synthetic scale-smoke invoice",
        "due_date": "2099-12-31",
        "lines": [{
            "description": "Synthetic legal services",
            "quantity_milli": 1000,
            "unit_price_piasters": 12500,
        }],
    }
    for index in range(INVOICE_COUNT):
        case_id = case_ids[index % len(case_ids)]
        _request(
            client, "post", "/cases/{}/invoices".format(case_id),
            json_body=invoice_payload,
        )
        if (index + 1) % 500 == 0:
            print("Created {} / {} invoices.".format(index + 1, INVOICE_COUNT), flush=True)
    print("Seeded {} invoices.".format(INVOICE_COUNT), flush=True)
    return case_ids


def run(data_dir, samples):
    original_env = dict(os.environ)
    runtime = None
    client = None
    try:
        _prepare_environment(data_dir)
        import app as app_module
        from database_runtime import DatabaseRuntime
        from fastapi.testclient import TestClient

        app_module._database_runtime = None
        runtime = DatabaseRuntime.from_env()
        runtime.initialize()
        firm_id, _ = runtime.provision_firm("Fictional Scale Smoke Firm")
        runtime.create_initial_firm_owner(
            firm_id,
            "Scale Smoke Owner",
            "scale-smoke-owner@example.test",
            app_module.hash_pw(SYNTHETIC_PASSWORD),
        )
        client = TestClient(app_module.app)
        login = client.post(
            "/login",
            json={"email": "scale-smoke-owner@example.test", "password": SYNTHETIC_PASSWORD},
        )
        if login.status_code != 200:
            raise RuntimeError("synthetic owner login failed: {}".format(login.text[:500]))

        case_ids = _seed(runtime, client, firm_id, app_module)
        search_body = {
            "q": SYNTHETIC_QUERY,
            "case_id": case_ids[0],
            "scope": "firm_documents",
        }
        search_probe = _request(client, "post", "/search", json_body=search_body)
        if not search_probe:
            raise RuntimeError("search smoke query returned no result for seeded passages")

        measurements = {
            "Dashboard": _measure(client, "get", "/dashboard", samples=samples),
            "Case list": _measure(client, "get", "/cases", samples=samples),
            "Case detail": _measure(client, "get", "/cases/{}".format(case_ids[0]), samples=samples),
            "Search": _measure(client, "post", "/search", samples=samples, json_body=search_body),
            "Invoice list": _measure(client, "get", "/invoices", samples=samples),
            "Finance overview": _measure(client, "get", "/finance/overview", samples=samples),
            "Firm export": _measure(client, "get", "/firm/data-export.zip", samples=max(3, samples // 6)),
        }
        print("\n| Endpoint | Samples | p50 (ms) | p95 (ms) |")
        print("|---|---:|---:|---:|")
        for name, result in measurements.items():
            print("| {} | {} | {:.1f} | {:.1f} |".format(
                name, result["samples"], result["p50"], result["p95"]
            ))
        print("\nTargets: dashboard, case list, case detail, invoice list and finance overview p95 < 300 ms; search p95 < 500 ms.")
        failures = []
        limits = {
            "Dashboard": 300,
            "Case list": 300,
            "Invoice list": 300,
            "Finance overview": 300,
            "Search": 500,
        }
        for name, limit in limits.items():
            result = measurements[name]
            if result["p95"] >= limit:
                failures.append("{} p95 {:.1f} ms >= {} ms".format(name, result["p95"], limit))
        if failures:
            print("PERFORMANCE TARGETS MISSED: " + "; ".join(failures), file=sys.stderr)
            return 2
        print("All latency targets met. Data directory: {}".format(data_dir))
        return 0
    finally:
        if client is not None:
            client.close()
        if runtime is not None:
            try:
                runtime.close_current_thread()
            except Exception:
                pass
        try:
            import app as app_module
            app_module._database_runtime = None
        except Exception:
            pass
        for key in tuple(os.environ):
            if key.startswith("COPILOT_") or key == "ADMIN_TOKEN":
                os.environ.pop(key, None)
        os.environ.update(original_env)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir",
        type=Path,
        help="empty directory for synthetic databases; omitted means a temporary directory",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=30,
        help="latency samples per endpoint (default: 30; firm export uses at least 3)",
    )
    args = parser.parse_args()
    if args.samples < 3 or args.samples > 200:
        parser.error("--samples must be between 3 and 200")
    if args.data_dir is not None:
        raise SystemExit(run(args.data_dir.resolve(), args.samples))
    with tempfile.TemporaryDirectory(prefix="legal-copilot-scale-smoke-") as temporary:
        raise SystemExit(run(Path(temporary), args.samples))


if __name__ == "__main__":
    main()
