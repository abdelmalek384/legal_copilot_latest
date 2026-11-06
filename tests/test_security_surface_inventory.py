"""Regression tests for the documented SEC-01 route and profile schema inventory."""
import os
import re
import sqlite3
import tempfile
from pathlib import Path

_TEST_DB_DIR = tempfile.TemporaryDirectory(prefix="legal-copilot-sec01-surface-")
os.environ["COPILOT_ENV"] = "development"
os.environ.pop("COPILOT_DB", None)
os.environ["COPILOT_CONTROL_DB"] = str(Path(_TEST_DB_DIR.name) / "control.sqlite3")
os.environ["COPILOT_TENANT_DB_ROOT"] = str(Path(_TEST_DB_DIR.name) / "tenants")
os.environ["COPILOT_CORPUS_DB"] = str(Path(_TEST_DB_DIR.name) / "corpus.sqlite3")
import app  # noqa: E402
from database_runtime import DatabaseRuntime  # noqa: E402

_RUNTIME = DatabaseRuntime.from_env()
_RUNTIME.initialize()
_INVENTORY_FIRM_ID, _INVENTORY_TENANT_PATH = _RUNTIME.provision_firm("SEC-01 Inventory Fixture")

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
    paths = (
        _RUNTIME.paths.control_plane,
        _INVENTORY_TENANT_PATH,
        _RUNTIME.paths.legal_corpus,
    )
    actual = set()
    for path in paths:
        uri = path.resolve().as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        try:
            rows = connection.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view') "
                "AND name NOT GLOB 'sqlite_*'"
            ).fetchall()
            actual.update(
                row[0] for row in rows
                if not (row[0].startswith("chunks_fts_") and row[0] != "chunks_fts")
            )
        finally:
            connection.close()
    assert documented == actual, f"Missing schema objects: {sorted(actual - documented)}; stale: {sorted(documented - actual)}"
