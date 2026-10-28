import unittest

from tools.audit_route_sql_access import audit_source


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
