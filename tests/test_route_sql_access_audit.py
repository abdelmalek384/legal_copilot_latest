import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.audit_route_sql_access import audit_source, main


class RouteSQLAccessAuditTests(unittest.TestCase):
    def test_maps_route_to_connection_boundary_and_referenced_table(self):
        source = '''
def conn():
    return None

def read_case(db):
    return db.execute("SELECT id,title FROM cases WHERE id=?", (1,)).fetchone()

@app.get("/cases/{case_id}")
def case_detail(case_id):
    db = conn()
    return read_case(db)
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 1)
        route = report["routes"][0]
        self.assertEqual((route["method"], route["path"], route["handler"]),
                         ("GET", "/cases/{case_id}", "case_detail"))
        self.assertEqual(route["data_boundaries"], ["firm"])
        self.assertIn("cases", route["table_references"])
        self.assertEqual(report["unclassified_sql_routes"], [])

    def test_flags_sql_routes_without_a_recognized_connection_boundary(self):
        source = '''
def execute_query(db):
    return db.execute("SELECT id FROM users").fetchall()

@app.get("/unsafe")
def unsafe():
    return execute_query(None)
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 1)
        self.assertEqual(report["unclassified_sql_routes"], ["GET /unsafe (unsafe)"])

    def test_reports_dynamic_sql_for_manual_review(self):
        source = '''
def conn():
    return None

def read_table(db, table):
    return db.execute(f"SELECT id FROM {table}").fetchall()

@app.get("/lookup")
def lookup():
    return read_table(conn(), "cases")
'''
        report = audit_source(source)
        self.assertEqual(report["dynamic_sql_call_count"], 1)
        self.assertEqual(report["routes_with_dynamic_sql"], [
            {"route": "GET /lookup (lookup)", "call_count": 1}
        ])
        site = report["routes"][0]["dynamic_sql_sites"][0]
        self.assertEqual(site["function"], "read_table")
        self.assertIn("{dynamic}", site["sql_template"])
        self.assertGreater(site["line"], 0)

    def test_resolves_finite_table_names_from_literal_loops(self):
        source = '''
def conn():
    return None

@app.delete("/cases/{case_id}")
def delete_case(case_id):
    db = conn()
    for table in ("chunks", "docs", "tasks"):
        db.execute("DELETE FROM %s WHERE case_id=?" % table, (case_id,))
'''
        report = audit_source(source)
        route = report["routes"][0]
        self.assertEqual(route["unresolved_sql_call_count"], 0)
        self.assertEqual(report["unresolved_sql_call_count"], 0)
        self.assertEqual(report["unclassified_sql_routes"], [])
        self.assertTrue({"chunks", "docs", "tasks"}.issubset(set(route["table_references"])))
        self.assertEqual(route["dynamic_sql_call_count"], 0)

    def test_resolves_sql_passed_to_local_lambda_and_reports_dynamic_join(self):
        source = '''
def corpus_conn():
    return None

@app.get("/cases/{case_id}")
def case_detail(case_id):
    db = corpus_conn()
    rows = lambda q: [dict(row) for row in db.execute(q, (case_id,))]
    result = rows("SELECT id FROM legal_documents WHERE document_id=?")
    where = []
    where.append("document_type = ?")
    sql = "SELECT id FROM legal_documents WHERE " + " AND ".join(where)
    return result, db.execute(sql, ("law",)).fetchall()
'''
        report = audit_source(source)
        self.assertEqual(report["unresolved_sql_call_count"], 0)
        self.assertEqual(report["routes"][0]["unresolved_sql_call_count"], 0)
        self.assertGreaterEqual(report["dynamic_sql_call_count"], 1)
        self.assertIn("legal_documents", report["routes"][0]["table_references"])

    def test_unreviewed_dynamic_sql_is_explicitly_reported(self):
        source = '''
def conn():
    return None

@app.get("/unsafe")
def unsafe(table):
    db = conn()
    return db.execute(f"SELECT id FROM {table}").fetchall()
'''
        report = audit_source(source)
        self.assertEqual(report["unresolved_sql_call_count"], 0)
        self.assertEqual(len(report["unreviewed_dynamic_sql_sites"]), 1)
        site = report["unreviewed_dynamic_sql_sites"][0]
        self.assertEqual(site["function"], "unsafe")
        self.assertIn("{dynamic}", site["sql_template"])

    def test_strict_cli_fails_for_unreviewed_dynamic_sql(self):
        source = '''
def conn():
    return None

@app.get("/unsafe")
def unsafe(table):
    db = conn()
    return db.execute(f"SELECT id FROM {table}").fetchall()
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "app.py"
            app_path.write_text(source, encoding="utf-8")
            output = io.StringIO()
            with patch("sys.argv", [
                "audit_route_sql_access.py", "--app", str(app_path), "--strict"
            ]), redirect_stdout(output):
                self.assertEqual(main(), 1)
            self.assertIn("UNREVIEWED DYNAMIC SQL", output.getvalue())
            self.assertIn("STRICT AUDIT FAILED", output.getvalue())

    def test_flags_direct_sqlite_open_in_route_call_graph(self):
        source = '''
import sqlite3
@app.get("/unsafe")
def unsafe():
    return sqlite3.connect("db.sqlite3")
'''
        report = audit_source(source)
        self.assertEqual(report["routes_opening_sqlite_directly"], ["GET /unsafe (unsafe)"])


if __name__ == "__main__":
    unittest.main()
