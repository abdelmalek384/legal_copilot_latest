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
DYNAMIC_ROUTE_REGISTRATION_METHODS = {"add_api_route", "add_route", "add_websocket_route", "mount"}
UNSUPPORTED_ROUTE_DECORATORS = {"route", "websocket", "websocket_route"}
# Public access is granted to an exact handler, not merely to a path.
# This prevents an unrelated route registered on a public URL from inheriting
# the exemption.
PUBLIC_ROUTES = {
    ("GET", "/", "home", "app.py"),
    ("GET", "/manifest.webmanifest", "pwa_manifest", "routers/platform.py"),
    ("GET", "/service-worker.js", "pwa_service_worker", "routers/platform.py"),
    ("GET", "/offline.html", "pwa_offline_page", "routers/platform.py"),
    ("GET", "/app-icon.svg", "pwa_app_icon", "routers/platform.py"),
    ("GET", "/app-icon.svg", "app_icon", "app.py"),
    ("GET", "/apple-touch-icon.png", "pwa_apple_touch_icon", "routers/platform.py"),
    ("GET", "/invite/accept", "invitation_accept_page", "routers/identity.py"),
    ("GET", "/account/recovery", "password_recovery_page", "routers/identity.py"),
    ("POST", "/login", "login", "app.py"),
    ("POST", "/invitations/accept/new", "accept_invitation_new_identity", "app.py"),
    ("POST", "/account/recovery/request", "request_account_recovery", "app.py"),
    ("POST", "/account/recovery/consume", "consume_account_recovery", "app.py"),
}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _framework_bindings(tree: ast.AST) -> set[str]:
    """Find FastAPI/APIRouter instances, including variables assigned through import aliases."""
    names = {"app", "router"}
    constructor_names = {"FastAPI", "APIRouter"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "fastapi":
            constructor_names.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name in {"FastAPI", "APIRouter"}
            )
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            targets = []
            value = None
            if isinstance(node, ast.Assign):
                targets = node.targets
                value = node.value
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
                value = node.value
            if isinstance(value, ast.Name) and value.id in constructor_names:
                for target in targets:
                    if isinstance(target, ast.Name) and target.id not in constructor_names:
                        constructor_names.add(target.id)
                        changed = True
                continue
            if isinstance(value, ast.Call):
                recognized = _call_name(value.func) in constructor_names
            else:
                recognized = isinstance(value, ast.Name) and value.id in names
            if not recognized:
                continue
            for target in targets:
                if isinstance(target, ast.Name) and target.id not in names:
                    names.add(target.id)
                    changed = True
    return names


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


def _unsupported_route_decorator(decorator: ast.AST, framework_names: set[str]) -> tuple[str, str] | None:
    """Identify valid framework route decorators this HTTP inventory cannot model."""
    if (
        not isinstance(decorator, ast.Call)
        or not isinstance(decorator.func, ast.Attribute)
        or not isinstance(decorator.func.value, ast.Name)
    ):
        return None
    owner = decorator.func.value.id
    method = decorator.func.attr.lower()
    if owner in framework_names and method in UNSUPPORTED_ROUTE_DECORATORS:
        return owner, method
    return None


def _route_methods(decorator: ast.AST, framework_names: set[str]) -> list[str]:
    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
        return []
    method = decorator.func.attr.lower()
    if method not in ROUTE_METHODS or not isinstance(decorator.func.value, ast.Name):
        return []
    if decorator.func.value.id not in framework_names:
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


def _route_path(decorator: ast.AST) -> str:
    if not isinstance(decorator, ast.Call):
        raise ValueError("route decorator must be a call")
    path_node = decorator.args[0] if decorator.args else next(
        (keyword.value for keyword in decorator.keywords if keyword.arg == "path"),
        None,
    )
    if not isinstance(path_node, ast.Constant) or not isinstance(path_node.value, str):
        raise ValueError("route path must be a literal string")
    return path_node.value


def audit_sources(
    sources: dict[str, str], *, require_public_routes: bool = True
) -> dict[str, Any]:
    routes: list[dict[str, Any]] = []
    findings: list[str] = []
    seen_public: set[tuple[str, str, str, str]] = set()

    for filename, source in sources.items():
        tree = ast.parse(source, filename=filename)
        framework_names = _framework_bindings(tree)
        for candidate in ast.walk(tree):
            if not isinstance(candidate, ast.Call) or not isinstance(candidate.func, ast.Attribute):
                continue
            owner = candidate.func.value
            if (
                isinstance(owner, ast.Name)
                and owner.id in framework_names
                and candidate.func.attr.lower() in DYNAMIC_ROUTE_REGISTRATION_METHODS
            ):
                findings.append(
                    f"cannot statically audit dynamic route registration "
                    f"{owner.id}.{candidate.func.attr} in {filename}; use literal route decorators"
                )
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                unsupported = _unsupported_route_decorator(decorator, framework_names)
                if unsupported is not None:
                    owner, method = unsupported
                    findings.append(
                        f"cannot statically audit unsupported route decorator "
                        f"{owner}.{method} on {node.name} in {filename}; "
                        "use supported literal HTTP route decorators"
                    )
                    continue
                try:
                    methods = _route_methods(decorator, framework_names)
                except ValueError as exc:
                    findings.append(
                        f"cannot statically audit HTTP methods for {node.name} in {filename}: {exc}"
                    )
                    continue
                if not methods:
                    continue
                try:
                    path = _route_path(decorator)
                except ValueError as exc:
                    findings.append(
                        f"cannot statically audit route path for {node.name} in {filename}: {exc}"
                    )
                    continue
                authenticated = (
                    _contains_user_dependency(node.args)
                    or _contains_user_dependency(decorator)
                )
                source_path = Path(filename)
                if not source_path.is_absolute():
                    source_path = ROOT / source_path
                try:
                    source_key = source_path.resolve().relative_to(ROOT).as_posix()
                except ValueError:
                    source_key = source_path.resolve().as_posix()
                for method in methods:
                    key = (method, path, node.name, source_key)
                    is_allowlisted = key in PUBLIC_ROUTES
                    duplicate_public = is_allowlisted and key in seen_public
                    is_public = is_allowlisted and not duplicate_public
                    if duplicate_public:
                        findings.append(
                            f"duplicate public route registration: {method} {path} "
                            f"({node.name}) in {source_key}"
                        )
                    elif is_public:
                        seen_public.add(key)
                    if not is_public and not authenticated:
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

    expected_public = {
        f"{method} {path} ({handler} in {source})"
        for method, path, handler, source in PUBLIC_ROUTES
    }
    observed_public = {
        f"{method} {path} ({handler} in {source})"
        for method, path, handler, source in seen_public
    }
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
        if isinstance(node, ast.ImportFrom):
            if (
                node.module
                and node.module.startswith("routers.")
                and any(alias.name == "router" for alias in node.names)
            ):
                modules.add(node.module)
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("routers."):
                    modules.add(alias.name)
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
        {str(args.app.resolve()): args.app.read_text(encoding="utf-8")}
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
