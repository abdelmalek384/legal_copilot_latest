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
ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "api_route"}
PUBLIC_ROUTES = {
    ("GET", "/"),
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
    if decorator.func.value.id != "app" or not decorator.args:
        return []
    if not isinstance(decorator.args[0], ast.Constant) or not isinstance(decorator.args[0].value, str):
        return []
    if method == "api_route":
        methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        for keyword in decorator.keywords:
            if keyword.arg == "methods" and isinstance(keyword.value, (ast.List, ast.Tuple, ast.Set)):
                methods = {
                    item.value.upper() for item in keyword.value.elts
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                }
        return sorted(methods)
    return [method.upper()]


def audit_source(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    routes: list[dict[str, Any]] = []
    findings: list[str] = []
    seen_public: set[tuple[str, str]] = set()

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            methods = _route_methods(decorator)
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
                    findings.append(f"{method} {path} ({node.name}) has no Depends(user) authentication")
                routes.append({
                    "method": method,
                    "path": path,
                    "handler": node.name,
                    "authentication": "public_allowlist" if is_public else ("Depends(user)" if authenticated else "missing"),
                })

    expected_public = {f"{method} {path}" for method, path in PUBLIC_ROUTES}
    observed_public = {f"{method} {path}" for method, path in seen_public}
    stale_public = sorted(expected_public - observed_public)
    if stale_public:
        findings.extend(f"public allowlist entry is no longer a registered route: {item}" for item in stale_public)

    routes.sort(key=lambda item: (item["path"], item["method"], item["handler"]))
    return {
        "route_count": len(routes),
        "authenticated_route_count": sum(item["authentication"] == "Depends(user)" for item in routes),
        "public_route_count": sum(item["authentication"] == "public_allowlist" for item in routes),
        "missing_authentication": sorted(findings),
        "routes": routes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, default=APP_FILE, help="FastAPI source file to audit")
    parser.add_argument("--strict", action="store_true", help="exit nonzero when authentication gaps exist")
    parser.add_argument("--json", action="store_true", help="emit the complete JSON inventory")
    args = parser.parse_args(argv)
    report = audit_source(args.app.read_text(encoding="utf-8"))
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
