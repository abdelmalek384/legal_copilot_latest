#!/usr/bin/env python3
"""Fail-closed static inventory of authentication dependencies on FastAPI routes.

This checks that every registered API route is authenticated by Depends(user),
except for a deliberately small, exact public-route allowlist. It is a guard
against accidental public-route regressions, not a substitute for authorization
and tenant-scope review inside authenticated handlers.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APP_FILE = ROOT / "app.py"
ROUTER_MODULES = {
    "routers.platform": ROOT / "routers" / "platform.py",
    "routers.identity": ROOT / "routers" / "identity.py",
}
ROUTER_FILES = tuple(ROUTER_MODULES.values())
ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "api_route"}
PUBLIC_ROUTES = {
    ("GET", "/"),
    ("GET", "/manifest.webmanifest"),
    ("GET", "/service-worker.js"),
    ("GET", "/offline.html"),
    ("GET", "/app-icon.svg"),
    ("GET", "/apple-touch-icon.png"),
    ("GET", "/invite/accept"),
    ("GET", "/account/recovery"),
    ("POST", "/login"),
    ("POST", "/invitations/accept/new"),
    ("POST", "/account/recovery/request"),
    ("POST", "/account/recovery/consume"),
}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_user_dependency(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and _call_name(node.func) == "Depends"
        and len(node.args) >= 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "user"
    )


def _contains_user_dependency(node: ast.AST) -> bool:
    return any(_is_user_dependency(item) for item in ast.walk(node))


def _route_methods(decorator: ast.AST) -> list[str]:
    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
        return []
    method = decorator.func.attr.lower()
    if method not in ROUTE_METHODS or not isinstance(decorator.func.value, ast.Name):
        return []
    if decorator.func.value.id not in {"app", "router"} or not decorator.args:
        return []
    if not isinstance(decorator.args[0], ast.Constant) or not isinstance(decorator.args[0].value, str):
        return []
    if method == "api_route":
        methods = {"GET"}
        for keyword in decorator.keywords:
            if keyword.arg != "methods":
                continue
            value = keyword.value
            if not isinstance(value, (ast.List, ast.Tuple, ast.Set)):
                raise ValueError("api_route methods must be a literal list, tuple, or set")
            if not value.elts:
                raise ValueError("api_route methods cannot be empty")
            parsed = []
            for item in value.elts:
                if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
                    raise ValueError("api_route methods must contain only literal strings")
                normalized = item.value.upper()
                if normalized not in {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE"}:
                    raise ValueError(f"api_route contains unsupported HTTP method {item.value!r}")
                parsed.append(normalized)
            methods = set(parsed)
        return sorted(methods)
    return [method.upper()]


def audit_sources(
    sources: dict[str, str], *, require_public_routes: bool = True
) -> dict[str, Any]:
    routes: list[dict[str, Any]] = []
    findings: list[str] = []
    seen_public: set[tuple[str, str]] = set()

    for filename, source in sources.items():
        tree = ast.parse(source, filename=filename)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                try:
                    methods = _route_methods(decorator)
                except ValueError as exc:
                    path = decorator.args[0].value if decorator.args and isinstance(decorator.args[0], ast.Constant) else "<dynamic>"
                    findings.append(
                        f"cannot statically audit HTTP methods for {path} ({node.name}) in {filename}: {exc}"
                    )
                    continue
                if not methods:
                    continue
                path = decorator.args[0].value
                authenticated = (
                    _contains_user_dependency(node.args)
                    or _contains_user_dependency(decorator)
                )
                for method in methods:
                    key = (method, path)
                    is_public = key in PUBLIC_ROUTES
                    if is_public:
                        seen_public.add(key)
                    elif not authenticated:
                        findings.append(
                            f"{method} {path} ({node.name}) in {filename} has no Depends(user) authentication"
                        )
                    routes.append({
                        "method": method,
                        "path": path,
                        "handler": node.name,
                        "source": filename,
                        "authentication": "public_allowlist" if is_public else ("Depends(user)" if authenticated else "missing"),
                    })

    expected_public = {f"{method} {path}" for method, path in PUBLIC_ROUTES}
    observed_public = {f"{method} {path}" for method, path in seen_public}
    stale_public = sorted(expected_public - observed_public)
    if require_public_routes and stale_public:
        findings.extend(f"public allowlist entry is no longer a registered route: {item}" for item in stale_public)

    routes.sort(key=lambda item: (item["path"], item["method"], item["handler"]))
    return {
        "route_count": len(routes),
        "authenticated_route_count": sum(item["authentication"] == "Depends(user)" for item in routes),
        "public_route_count": sum(item["authentication"] == "public_allowlist" for item in routes),
        "missing_authentication": sorted(findings),
        "routes": routes,
    }


def audit_source(source: str) -> dict[str, Any]:
    """Compatibility helper for focused, single-module synthetic tests."""
    return audit_sources({"app.py": source}, require_public_routes=False)


def imported_router_modules(source: str) -> set[str]:
    """Discover router modules imported by app.py so new routers cannot evade the audit."""
    tree = ast.parse(source, filename=str(APP_FILE))
    modules = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if node.module.startswith("routers.") and any(alias.name == "router" for alias in node.names):
            modules.add(node.module)
    return modules


def default_sources() -> dict[str, str]:
    app_source = APP_FILE.read_text(encoding="utf-8")
    imported = imported_router_modules(app_source)
    unregistered = sorted(imported - set(ROUTER_MODULES))
    if unregistered:
        raise RuntimeError(
            "route-authentication audit has no source mapping for imported routers: "
            + ", ".join(unregistered)
        )
    paths = (APP_FILE, *(ROUTER_MODULES[module] for module in sorted(imported)))
    return {
        str(path.relative_to(ROOT)): (
            app_source if path == APP_FILE else path.read_text(encoding="utf-8")
        )
        for path in paths
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=None, help="Audit only this FastAPI source file (primarily for focused checks)")
    parser.add_argument("--strict", action="store_true", help="exit nonzero when authentication gaps exist")
    parser.add_argument("--json", action="store_true", help="emit the complete JSON inventory")
    args = parser.parse_args(argv)
    sources = (
        {args.app.name: args.app.read_text(encoding="utf-8")}
        if args.app is not None else default_sources()
    )
    report = audit_sources(sources)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"routes={report['route_count']} authenticated={report['authenticated_route_count']} "
            f"public_allowlisted={report['public_route_count']} "
            f"missing_auth={len(report['missing_authentication'])}"
        )
        for finding in report["missing_authentication"]:
            print(f"ERROR: {finding}")
    return 1 if args.strict and report["missing_authentication"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
