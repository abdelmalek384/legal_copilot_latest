"""Read-only inventory of database DDL still embedded in application startup.

This tool inspects source files only. It never opens or modifies a database.
Usage: python scripts/database_startup_ddl_inventory.py [--app app.py] [--migrations-dir migrations]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

DDL_PATTERN = re.compile(
    r"\b(CREATE\s+VIRTUAL\s+TABLE|CREATE\s+TABLE|CREATE\s+INDEX|ALTER\s+TABLE|DROP\s+TABLE|DROP\s+INDEX)\b",
    re.IGNORECASE,
)
TABLE_PATTERN = re.compile(
    r"\b(?:TABLE|INDEX)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?[\\"'`]?([A-Za-z_][A-Za-z0-9_]*)",
    re.IGNORECASE,
)


def _schema_assignment(tree: ast.Module) -> ast.Assign:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SCHEMA"
            for target in node.targets
        ):
            return node
    raise ValueError("Could not find a literal SCHEMA assignment in app.py")


def _statements(sql: str) -> list[str]:
    # These migrations contain ordinary SQLite DDL statements ending in semicolons.
    return [part.strip() for part in sql.split(";") if part.strip()]


def _classify(sql: str) -> dict[str, Any]:
    counts = {"create_table": 0, "create_virtual_table": 0, "create_index": 0,
              "alter_table": 0, "drop_table": 0, "drop_index": 0}
    objects: list[dict[str, str]] = []
    for statement in _statements(sql):
        match = DDL_PATTERN.search(statement)
        if not match:
            continue
        verb = re.sub(r"\s+", " ", match.group(1).lower())
        key = verb.replace(" ", "_")
        counts[key] += 1
        table = TABLE_PATTERN.search(statement)
        if table:
            objects.append({"operation": verb, "object": table.group(1)})
    return {"counts": counts, "objects": objects}


def inventory(app_path: str | Path, migrations_dir: str | Path) -> dict[str, Any]:
    app_path = Path(app_path)
    source = app_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(app_path))
    assignment = _schema_assignment(tree)
    schema = ast.literal_eval(assignment.value)
    if not isinstance(schema, str):
        raise ValueError("SCHEMA must be a string literal to inventory safely")

    schema_inventory = _classify(schema)
    schema_lines = set(range(assignment.lineno, assignment.end_lineno + 1))
    startup_operations: list[dict[str, Any]] = []
    for number, line in enumerate(source.splitlines(), start=1):
        if number in schema_lines:
            continue
        match = DDL_PATTERN.search(line)
        if not match:
            continue
        verb = re.sub(r"\s+", " ", match.group(1).lower())
        obj = TABLE_PATTERN.search(line)
        startup_operations.append({
            "line": number,
            "operation": verb,
            "object": obj.group(1) if obj else None,
            "source": line.strip()[:220],
        })

    migration_entries = []
    directory = Path(migrations_dir)
    for path in sorted(directory.glob("*.sql")):
        classified = _classify(path.read_text(encoding="utf-8"))
        migration_entries.append({
            "file": path.name,
            **classified,
        })

    return {
        "mode": "source_only_read_only",
        "database_opened": False,
        "app_file": str(app_path),
        "startup_schema": schema_inventory,
        "startup_ddl_outside_schema_literal": startup_operations,
        "migrations": migration_entries,
        "limitations": [
            "Static source inventory; it does not inspect a live database or prove runtime execution paths.",
            "Dynamic SQL and DDL assembled across multiple strings may require manual review.",
            "Legacy startup DDL must not be moved until fresh-install and upgrade ordering is tested on representative copies.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--app", type=Path, default=root / "app.py")
    parser.add_argument("--migrations-dir", type=Path, default=root / "migrations")
    args = parser.parse_args(argv)
    print(json.dumps(inventory(args.app, args.migrations_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
