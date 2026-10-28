#!/usr/bin/env python3
"""Static route-to-SQL access map for the tenant-isolation review.

This is a review aid, not a proof of authorization. It follows local function calls
from registered FastAPI handlers, records recognized connection-boundary helpers,
and inventories SQL table references. Dynamic SQL and indirect framework dependencies
must still be reviewed manually.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
APP_FILE = ROOT / "app.py"
ROUTE_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "api_route"}
BOUNDARY_CALLS = {
    "conn": "firm",
    "firm_connection": "firm",
    "control_conn": "control_plane",
    "control_connection": "control_plane",
    "corpus_conn": "legal_corpus",
    "legal_corpus_connection": "legal_corpus",
    "_legacy_conn": "legacy_compatibility",
    "_original_file_store": "original_file_storage",
}
STOP_TRAVERSAL = {
    "conn", "control_conn", "corpus_conn", "_legacy_conn",
    "get_database_runtime", "_original_file_store",
}
TABLE_PATTERNS = (
    re.compile(r"""\b(?:FROM|JOIN|INTO|UPDATE|TABLE|REFERENCES)\s+["'`]?([A-Za-z_][A-Za-z0-9_]*)""", re.I),
    re.compile(r"""\bDELETE\s+FROM\s+["'`]?([A-Za-z_][A-Za-z0-9_]*)""", re.I),
    re.compile(r"""\bPRAGMA\s+(?:table_info|foreign_key_check)\s*\(\s*["'`]?([A-Za-z_][A-Za-z0-9_]*)""", re.I),
)


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _route_decorators(function: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    result = []
    for decorator in function.decorator_list:
        if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
            continue
        owner = decorator.func.value
        method = decorator.func.attr.lower()
        if not isinstance(owner, ast.Name) or owner.id != "app" or method not in ROUTE_METHODS:
            continue
        if not decorator.args or not isinstance(decorator.args[0], ast.Constant):
            continue
        path = decorator.args[0].value
        if not isinstance(path, str):
            continue
        if method == "api_route":
            methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
            for keyword in decorator.keywords:
                if keyword.arg == "methods" and isinstance(keyword.value, (ast.List, ast.Tuple)):
                    methods = {
                        item.value.upper() for item in keyword.value.elts
                        if isinstance(item, ast.Constant) and isinstance(item.value, str)
                    }
            result.extend({"method": item, "path": path} for item in sorted(methods))
        else:
            result.append({"method": method.upper(), "path": path})
    return result


def _sql_text(node: ast.AST | None) -> tuple[str, bool]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, False
    if isinstance(node, ast.JoinedStr):
        pieces = []
        dynamic = False
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                pieces.append(value.value)
            else:
                dynamic = True
        return " ".join(pieces), dynamic
    return "", True


def _tables_in(sql: str) -> set[str]:
    tables: set[str] = set()
    for pattern in TABLE_PATTERNS:
        tables.update(match.group(1).strip('"\u0060').lower() for match in pattern.finditer(sql))
    return tables


def audit_source(source: str) -> dict[str, Any]:
    tree = ast.parse(source, filename=str(APP_FILE))
    functions = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    routes: list[tuple[dict[str, str], str]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for route in _route_decorators(node):
                routes.append((route, node.name))

    records = []
    for route, handler in sorted(routes, key=lambda item: (item[0]["path"], item[0]["method"])):
        pending = [handler]
        visited: set[str] = set()
        helpers: set[str] = set()
        boundaries: set[str] = set()
        tables: set[str] = set()
        sql_calls = 0
        dynamic_sql_calls = 0
        direct_sqlite_open = False

        while pending:
            name = pending.pop()
            if name in visited or name not in functions:
                continue
            visited.add(name)
            node = functions[name]
            for call in (item for item in ast.walk(node) if isinstance(item, ast.Call)):
                called = _call_name(call.func)
                if called in BOUNDARY_CALLS:
                    helpers.add(called)
                    boundaries.add(BOUNDARY_CALLS[called])
                if called == "connect" and isinstance(call.func, ast.Attribute):
                    owner = call.func.value
                    if isinstance(owner, ast.Name) and owner.id == "sqlite3":
                        direct_sqlite_open = True
                if called in {"execute", "executemany", "executescript"}:
                    sql, dynamic = _sql_text(call.args[0] if call.args else None)
                    if sql or dynamic:
                        sql_calls += 1
                        tables.update(_tables_in(sql))
                        dynamic_sql_calls += int(dynamic)
                if called in functions and called not in STOP_TRAVERSAL and called not in visited:
                    pending.append(called)

        records.append({
            **route,
            "handler": handler,
            "reachable_local_functions": sorted(visited),
            "connection_helpers": sorted(helpers),
            "data_boundaries": sorted(boundaries),
            "sql_call_count": sql_calls,
            "dynamic_sql_call_count": dynamic_sql_calls,
            "table_references": sorted(tables),
            "direct_sqlite_open": direct_sqlite_open,
        })

    unclassified_sql = [
        f"{row['method']} {row['path']} ({row['handler']})"
        for row in records
        if row["sql_call_count"] and not row["data_boundaries"]
    ]
    direct_open = [
        f"{row['method']} {row['path']} ({row['handler']})"
        for row in records if row["direct_sqlite_open"]
    ]
    dynamic_sql = [
        {
            "route": f"{row['method']} {row['path']} ({row['handler']})",
            "call_count": row["dynamic_sql_call_count"],
        }
        for row in records if row["dynamic_sql_call_count"]
    ]
    return {
        "scope": "static review aid; not proof of authorization or complete runtime SQL coverage",
        "route_count": len(records),
        "routes_with_sql": sum(bool(row["sql_call_count"]) for row in records),
        "dynamic_sql_call_count": sum(row["dynamic_sql_call_count"] for row in records),
        "routes_with_dynamic_sql": dynamic_sql,
        "unclassified_sql_routes": unclassified_sql,
        "routes_opening_sqlite_directly": direct_open,
        "routes": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit the complete machine-readable map.")
    parser.add_argument("--app", type=Path, default=APP_FILE, help="Application source file to inspect.")
    args = parser.parse_args()
    report = audit_source(args.app.read_text(encoding="utf-8"))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(
            f"Route SQL access map: routes={report['route_count']}, "
            f"routes_with_sql={report['routes_with_sql']}, "
            f"dynamic_sql_calls={report['dynamic_sql_call_count']}, "
            f"unclassified_sql_routes={len(report['unclassified_sql_routes'])}, "
            f"direct_sqlite_opens={len(report['routes_opening_sqlite_directly'])}"
        )
        for item in report["routes_with_dynamic_sql"]:
            print(f"DYNAMIC SQL REVIEW REQUIRED ({item['call_count']} call(s)): {item['route']}")
        for item in report["unclassified_sql_routes"]:
            print(f"UNCLASSIFIED SQL: {item}")
        for item in report["routes_opening_sqlite_directly"]:
            print(f"DIRECT SQLITE OPEN: {item}")
    return 1 if report["unclassified_sql_routes"] or report["routes_opening_sqlite_directly"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
