#!/usr/bin/env python3
"""Read-only HTTP smoke test for a deployed Legal Copilot public shell.

The probe sends only unauthenticated GET requests to fixed public PWA assets.
It never submits credentials, calls authenticated APIs, or mutates application data.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx


PUBLIC_ASSETS = {
    "/": "text/html",
    "/manifest.webmanifest": "application/manifest+json",
    "/service-worker.js": "javascript",
    "/offline.html": "text/html",
    "/app-icon.svg": "image/svg+xml",
    "/apple-touch-icon.png": "image/png",
}


def normalize_base_url(value: str, *, allow_http_loopback: bool = False) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("base URL is required")
    try:
        parsed = urlsplit(value.strip())
        host = parsed.hostname
        _ = parsed.port
    except ValueError as exc:
        raise ValueError("base URL is malformed") from exc
    if (
        not host
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("base URL must be an origin only, without credentials, path, query, or fragment")
    if parsed.scheme == "https":
        pass
    elif parsed.scheme == "http" and allow_http_loopback:
        try:
            loopback = host.lower().rstrip(".") == "localhost" or ipaddress.ip_address(host).is_loopback
        except ValueError:
            loopback = False
        if not loopback:
            raise ValueError("plain HTTP is allowed only for loopback when explicitly enabled")
    else:
        raise ValueError("HTTPS is required; HTTP is permitted only for explicit loopback testing")
    return f"{parsed.scheme}://{parsed.netloc}"


def run_smoke(
    base_url: str,
    *,
    client: httpx.Client | None = None,
    allow_http_loopback: bool = False,
) -> dict:
    checks: list[dict] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    try:
        origin = normalize_base_url(base_url, allow_http_loopback=allow_http_loopback)
    except ValueError as exc:
        record("base_url", False, str(exc))
        return {"ready": False, "base_url": "", "checks": checks}

    own_client = client is None
    http = client or httpx.Client(timeout=10.0, follow_redirects=False)
    responses = {}
    try:
        for path, expected_type in PUBLIC_ASSETS.items():
            try:
                response = http.get(origin + path)
            except httpx.HTTPError as exc:
                record(f"GET {path}", False, f"request failed: {type(exc).__name__}")
                continue
            responses[path] = response
            record(
                f"GET {path}",
                response.status_code == 200,
                f"HTTP {response.status_code}",
            )
            content_type = response.headers.get("content-type", "").lower()
            record(
                f"content-type {path}",
                expected_type in content_type,
                content_type or "missing Content-Type",
            )
            for header, expected in (
                ("cache-control", "no-store"),
                ("x-content-type-options", "nosniff"),
                ("x-frame-options", "deny"),
                ("referrer-policy", "no-referrer"),
            ):
                value = response.headers.get(header, "").lower()
                record(
                    f"{header} {path}",
                    expected in value,
                    value or "missing security header",
                )
            csp = response.headers.get("content-security-policy", "")
            record(
                f"content-security-policy {path}",
                "default-src 'self'" in csp and "worker-src 'self'" in csp,
                "required same-origin script/worker policy present" if (
                    "default-src 'self'" in csp and "worker-src 'self'" in csp
                ) else "missing required default-src or worker-src directive",
            )
            if origin.startswith("https://"):
                record(
                    f"strict-transport-security {path}",
                    bool(response.headers.get("strict-transport-security")),
                    "HSTS present" if response.headers.get("strict-transport-security") else "HSTS missing",
                )

        root = responses.get("/")
        if root is not None and root.status_code == 200:
            record(
                "root manifest link",
                'rel="manifest" href="/manifest.webmanifest"' in root.text,
                "manifest link present" if 'rel="manifest" href="/manifest.webmanifest"' in root.text else "manifest link missing",
            )
            record(
                "root service-worker registration",
                'navigator.serviceWorker.register("/service-worker.js")' in root.text,
                "service worker registration present" if 'navigator.serviceWorker.register("/service-worker.js")' in root.text else "service worker registration missing",
            )

        manifest_response = responses.get("/manifest.webmanifest")
        if manifest_response is not None and manifest_response.status_code == 200:
            try:
                manifest = manifest_response.json()
                valid_manifest = (
                    manifest.get("lang") == "ar"
                    and manifest.get("dir") == "rtl"
                    and manifest.get("display") == "standalone"
                    and manifest.get("start_url") == "/"
                    and isinstance(manifest.get("icons"), list)
                    and bool(manifest["icons"])
                )
            except (ValueError, AttributeError, TypeError):
                valid_manifest = False
            record(
                "Arabic install manifest",
                valid_manifest,
                "Arabic RTL standalone manifest present" if valid_manifest else "manifest is invalid or missing required Arabic/install fields",
            )

        worker = responses.get("/service-worker.js")
        if worker is not None and worker.status_code == 200:
            body = worker.text
            safe_worker = (
                'cache.add(OFFLINE_URL)' in body
                and 'request.mode === "navigate" && url.pathname === "/"' in body
                and "caches.put(" not in body
                and "cache.addAll(" not in body
                and "caches.match(OFFLINE_URL)" not in body
            )
            record(
                "service-worker cache boundary",
                safe_worker,
                "static offline notice only; API and matter responses are not cached" if safe_worker else "unexpected cache behavior in service worker",
            )
            record(
                "service-worker root scope",
                worker.headers.get("service-worker-allowed") == "/",
                worker.headers.get("service-worker-allowed", "Service-Worker-Allowed missing"),
            )

        offline = responses.get("/offline.html")
        if offline is not None and offline.status_code == 200:
            record(
                "offline privacy notice",
                "not stored for offline use" in offline.text.lower(),
                "offline notice explains that account/matter data are not cached" if "not stored for offline use" in offline.text.lower() else "offline privacy warning missing",
            )

    finally:
        if own_client:
            http.close()

    return {
        "ready": bool(checks) and all(item["passed"] for item in checks),
        "base_url": origin,
        "checks": checks,
        "passed": sum(1 for item in checks if item["passed"]),
        "failed": sum(1 for item in checks if not item["passed"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Deployed HTTPS origin, e.g. https://legal.example.com")
    parser.add_argument("--allow-http-loopback", action="store_true", help="Permit HTTP only for localhost/loopback smoke tests")
    parser.add_argument("--out", help="Optional path for a sanitized JSON report")
    args = parser.parse_args(argv)
    report = run_smoke(args.base_url, allow_http_loopback=args.allow_http_loopback)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
