"""Regression tests for the documented SEC-01 route and schema inventory."""
import os
import re
import tempfile
from pathlib import Path

os.environ["COPILOT_DB"] = os.path.join(tempfile.gettempdir(), "legal-copilot-sec01-surface-test.db")
import app  # noqa: E402

INVENTORY = Path(__file__).resolve().parents[1] / "docs" / "sec-01-attack-surface-inventory.md"


def test_routes_match_documented_inventory():
    markdown = INVENTORY.read_text(encoding="utf-8")
    section = markdown.split("## HTTP route inventory", 1)[1].split("## Database table inventory", 1)[0]
    documented = set(re.findall(r"\| `([A-Z]+)` \| `([^`]+)` \|", section))
    registered = set()
    for route in app.app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None) or set()
        if not path or path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
            continue
        for method in methods - {"HEAD", "OPTIONS"}:
            registered.add((method, path))
    assert documented == registered, f"Missing routes: {sorted(registered - documented)}; stale: {sorted(documented - registered)}"


def test_schema_objects_match_documented_inventory():
    markdown = INVENTORY.read_text(encoding="utf-8")
    section = markdown.split("## Database table inventory", 1)[1].split("## Cross-cutting surfaces", 1)[0]
    documented = set(re.findall(r"\| `([A-Za-z_][A-Za-z0-9_]*)` \|", section))
    connection = app.conn()
    try:
        rows = connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'").fetchall()
        actual = {row[0] for row in rows if not (row[0].startswith("chunks_fts_") and row[0] != "chunks_fts")}
    finally:
        connection.close()
    assert documented == actual, f"Missing schema objects: {sorted(actual - documented)}; stale: {sorted(documented - actual)}"
