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


def _sql_text(
    node: ast.AST | None,
    *,
    assignments: dict[str, list[ast.AST]] | None = None,
    globals_: dict[str, ast.AST] | None = None,
    seen: frozenset[str] = frozenset(),
    mutated_names: set[str] | None = None,
) -> tuple[str, bool, bool]:
    """Return (template, interpolated, resolved) for a SQL expression."""
    assignments = assignments or {}
    globals_ = globals_ or {}
    mutated_names = mutated_names or set()
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value, False, True
    if isinstance(node, ast.JoinedStr):
        pieces = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                pieces.append(value.value)
            else:
                pieces.append("{dynamic}")
        return "".join(pieces), True, True
    if isinstance(node, ast.Name):
        name = node.id
        if name in seen:
            return "{unresolved:" + name + "}", False, False
        if name in assignments and name not in mutated_names:
            values = assignments[name]
            resolved = [
                _sql_text(value, assignments=assignments, globals_=globals_, seen=seen | {name}, mutated_names=mutated_names)
                for value in values
            ]
            if len(resolved) == 1:
                return resolved[0]
            if resolved and all(item[2] and not item[1] for item in resolved):
                unique = list(dict.fromkeys(item[0] for item in resolved))
                if len(unique) == 1:
                    return unique[0], False, True
                return "{choice}".join(unique), False, True
        if name in globals_:
            return _sql_text(globals_[name], globals_=globals_, seen=seen | {name}, mutated_names=mutated_names)
        return "{unresolved:" + name + "}", False, False
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, left_dynamic, left_resolved = _sql_text(
            node.left, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names
        )
        right, right_dynamic, right_resolved = _sql_text(
            node.right, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names
        )
        return left + right, left_dynamic or right_dynamic, left_resolved and right_resolved
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        left, left_dynamic, left_resolved = _sql_text(
            node.left, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names
        )
        right, _, right_resolved = _sql_text(
            node.right, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names
        )
        if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
            # Preserve finite, literal loop substitutions as separate SQL
            # alternatives so table inventory can see every referenced table.
            if isinstance(node.right, ast.Name):
                values = assignments.get(node.right.id, [])
                literals = [
                    value.value for value in values
                    if isinstance(value, ast.Constant) and isinstance(value.value, str)
                ]
                if literals and len(literals) == len(values):
                    try:
                        alternatives = [node.left.value % value for value in dict.fromkeys(literals)]
                    except (TypeError, ValueError):
                        alternatives = []
                    if alternatives:
                        return "{choice}".join(alternatives), True, True
            template = re.sub(r"%[sdif]", "{dynamic}", left)
            return template, True, right_resolved
        return left + " {dynamic} " + right, True, left_resolved and right_resolved
    if isinstance(node, ast.IfExp):
        body, body_dynamic, body_resolved = _sql_text(
            node.body, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names
        )
        other, other_dynamic, other_resolved = _sql_text(
            node.orelse, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names
        )
        if body_resolved and other_resolved:
            return body + "{choice}" + other, body_dynamic or other_dynamic, True
        return body + "{choice}" + other, body_dynamic or other_dynamic, False
    if isinstance(node, (ast.List, ast.Tuple)):
        parts = [
            _sql_text(item, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names)
            for item in node.elts
        ]
        if all(item[2] for item in parts):
            return "".join(item[0] for item in parts), any(item[1] for item in parts), True
        return "{unresolved:sequence}", False, False
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == "format" and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str):
            template = re.sub(r"\{[^{}]*\}", "{dynamic}", node.func.value.value)
            return template, bool(node.args or node.keywords), True
        if node.func.attr == "join" and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str):
            if node.args and isinstance(node.args[0], (ast.List, ast.Tuple)):
                parts = [
                    _sql_text(item, assignments=assignments, globals_=globals_, seen=seen, mutated_names=mutated_names)
                    for item in node.args[0].elts
                ]
                if all(item[2] for item in parts):
                    return node.func.value.value.join(item[0] for item in parts), any(item[1] for item in parts), True
            # Joining a runtime-built list is dynamic SQL, but the surrounding
            # expression is understood. Keep it visible for manual review rather
            # than misclassifying the entire SQL statement as unresolved.
            if node.args:
                return "{dynamic_join}", True, True
        return "{unresolved:call}", False, False
    return "{unresolved:expression}", False, False


def _assignments_for(node: ast.AST) -> dict[str, list[ast.AST]]:
    assignments: dict[str, list[ast.AST]] = {}
    for item in ast.walk(node):
        if isinstance(item, ast.Assign):
            targets, value = item.targets, item.value
        elif isinstance(item, ast.AnnAssign):
            targets, value = [item.target], item.value
        else:
            targets, value = [], None
        for target in targets:
            if isinstance(target, ast.Name) and value is not None:
                assignments.setdefault(target.id, []).append(value)
        # Resolve finite loop domains, for example table names in a literal tuple.
        # This is a static inventory aid and never executes the loop.
        if isinstance(item, (ast.For, ast.AsyncFor)) and isinstance(item.target, ast.Name):
            iterable = item.iter
            if isinstance(iterable, (ast.List, ast.Tuple)) and all(
                isinstance(element, ast.Constant) and isinstance(element.value, str)
                for element in iterable.elts
            ):
                assignments.setdefault(item.target.id, []).extend(iterable.elts)
    return assignments


def _lambda_parameter_values(node: ast.AST) -> dict[str, list[ast.AST]]:
    """Resolve literal arguments passed to locally assigned lambdas, for SQL inventory."""
    result: dict[str, list[ast.AST]] = {}
    lambdas: dict[str, ast.Lambda] = {}
    for item in ast.walk(node):
        if not isinstance(item, ast.Assign) or not isinstance(item.value, ast.Lambda):
            continue
        for target in item.targets:
            if isinstance(target, ast.Name):
                lambdas[target.id] = item.value
    if not lambdas:
        return result
    for item in ast.walk(node):
        if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Name):
            continue
        lambda_node = lambdas.get(item.func.id)
        if lambda_node is None:
            continue
        for parameter, argument in zip(lambda_node.args.args, item.args):
            result.setdefault(parameter.arg, []).append(argument)
    return result


def _mutated_sql_names(node: ast.AST) -> set[str]:
    mutated = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Call) and isinstance(item.func, ast.Attribute):
            if item.func.attr in {"append", "extend", "insert", "clear", "pop", "remove"}:
                owner = item.func.value
                if isinstance(owner, ast.Name):
                    mutated.add(owner.id)
    return mutated


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
    global_assignments: dict[str, ast.AST] = {}
    for item in tree.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    global_assignments[target.id] = item.value
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name) and item.value is not None:
            global_assignments[item.target.id] = item.value
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
        dynamic_sql_sites: list[dict[str, Any]] = []
        unresolved_sql_sites: list[dict[str, Any]] = []
        direct_sqlite_open = False

        while pending:
            name = pending.pop()
            if name in visited or name not in functions:
                continue
            visited.add(name)
            node = functions[name]
            local_assignments = _assignments_for(node)
            for parameter, values in _lambda_parameter_values(node).items():
                local_assignments.setdefault(parameter, []).extend(values)
            mutated_sql_names = _mutated_sql_names(node)
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
                    sql, dynamic, resolved = _sql_text(
                        call.args[0] if call.args else None,
                        assignments=local_assignments,
                        globals_=global_assignments,
                        mutated_names=mutated_sql_names,
                    )
                    if sql or dynamic or not resolved:
                        sql_calls += 1
                        tables.update(_tables_in(sql))
                        dynamic_sql_calls += int(dynamic)
                        site = {
                            "function": name,
                            "line": call.lineno,
                            "sql_template": sql[:1000],
                        }
                        if dynamic:
                            dynamic_sql_sites.append(site)
                        if not resolved:
                            unresolved_sql_sites.append(site)
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
            "dynamic_sql_sites": sorted(dynamic_sql_sites, key=lambda site: (site["function"], site["line"])),
            "unresolved_sql_call_count": len(unresolved_sql_sites),
            "unresolved_sql_sites": sorted(unresolved_sql_sites, key=lambda site: (site["function"], site["line"])),
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
        "unresolved_sql_call_count": sum(row["unresolved_sql_call_count"] for row in records),
        "routes_with_dynamic_sql": dynamic_sql,
        "unclassified_sql_routes": unclassified_sql,
        "routes_opening_sqlite_directly": direct_open,
        "routes": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit the complete machine-readable map.")
    parser.add_argument("--strict", action="store_true", help="Fail on unresolved SQL, unclassified SQL routes, or direct SQLite opens.")
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
            f"unresolved_sql_calls={report['unresolved_sql_call_count']}, "
            f"unclassified_sql_routes={len(report['unclassified_sql_routes'])}, "
            f"direct_sqlite_opens={len(report['routes_opening_sqlite_directly'])}"
        )
        for row in report["routes"]:
            for site in row["dynamic_sql_sites"]:
                print(
                    f"DYNAMIC SQL REVIEW REQUIRED: {row['method']} {row['path']} "
                    f"({site['function']}:{site['line']}): {site['sql_template']}"
                )
            for site in row["unresolved_sql_sites"]:
                print(
                    f"UNRESOLVED SQL EXPRESSION: {row['method']} {row['path']} "
                    f"({site['function']}:{site['line']}): {site['sql_template']}"
                )
        for item in report["unclassified_sql_routes"]:
            print(f"UNCLASSIFIED SQL: {item}")
        for item in report["routes_opening_sqlite_directly"]:
            print(f"DIRECT SQLITE OPEN: {item}")
    failed = bool(report["unclassified_sql_routes"] or report["routes_opening_sqlite_directly"])
    if args.strict:
        failed = failed or bool(report["unresolved_sql_call_count"])
        if report["unresolved_sql_call_count"]:
            print("STRICT AUDIT FAILED: unresolved SQL expressions require explicit review.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
