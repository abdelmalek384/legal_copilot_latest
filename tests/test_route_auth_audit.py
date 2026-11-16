import tempfile
import unittest
from pathlib import Path

from tools.audit_route_auth import (
    APP_FILE, ROUTER_FILES, ROUTER_MODULES, PUBLIC_ROUTES,
    audit_source, audit_sources, imported_router_modules, main,
)


class RouteAuthenticationAuditTests(unittest.TestCase):
    def test_current_application_has_authentication_on_every_non_public_route(self):
        sources = {str(APP_FILE): APP_FILE.read_text(encoding="utf-8")}
        sources.update({str(path): path.read_text(encoding="utf-8") for path in ROUTER_FILES})
        report = audit_sources(sources)
        self.assertGreater(report["route_count"], 100)
        self.assertEqual(report["public_route_count"], len(PUBLIC_ROUTES))
        self.assertEqual(report["missing_authentication"], [])

    def test_current_app_router_imports_are_all_explicitly_audited(self):
        source = APP_FILE.read_text(encoding="utf-8")
        imported = imported_router_modules(source)
        self.assertEqual(imported, set(ROUTER_MODULES))
        self.assertEqual(set(ROUTER_FILES), set(ROUTER_MODULES.values()))

    def test_new_unregistered_router_import_is_detected(self):
        source = "from routers.new_feature import router as feature_router\n"
        imported = imported_router_modules(source)
        self.assertEqual(imported, {"routers.new_feature"})
        self.assertFalse(imported.issubset(set(ROUTER_MODULES)))

    def test_flags_route_without_user_dependency(self):
        source = '''
def user():
    pass

@app.get("/private")
def private():
    return {"secret": True}
'''
        report = audit_source(source)
        self.assertEqual(report["missing_authentication"], [
            "GET /private (private) in app.py has no Depends(user) authentication"
        ])

    def test_accepts_dependency_in_multiline_signature(self):
        source = '''
def user():
    pass

@app.get("/private")
def private(
    item_id: int,
    current: dict = Depends(user),
):
    return item_id
'''
        report = audit_source(source)
        self.assertEqual(report["missing_authentication"], [])
        self.assertEqual(report["authenticated_route_count"], 1)

    def test_expands_api_route_methods_and_requires_each_method_to_be_reviewed(self):
        source = '''
@app.api_route("/private", methods=["GET", "POST"])
def private():
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["missing_authentication"], [
            "GET /private (private) in app.py has no Depends(user) authentication",
            "POST /private (private) in app.py has no Depends(user) authentication",
        ])

    def test_api_route_without_methods_defaults_to_get_only(self):
        source = '''
def user():
    pass

@app.api_route("/private")
def private(current: dict = Depends(user)):
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 1)
        self.assertEqual(report["routes"][0]["method"], "GET")
        self.assertEqual(report["missing_authentication"], [])

    def test_public_allowlist_must_match_registered_routes(self):
        source = '''
@app.get("/")
def home():
    return "ok"
'''
        from tools.audit_route_auth import audit_sources
        report = audit_sources({"app.py": source}, require_public_routes=True)
        self.assertTrue(any("public allowlist entry is no longer a registered route" in item
                            for item in report["missing_authentication"]))

    def test_dynamic_api_route_methods_fail_closed(self):
        source = '''
def user():
    pass

METHODS = ["GET", "POST"]
@app.api_route("/private", methods=METHODS)
def private(current: dict = Depends(user)):
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 0)
        self.assertEqual(len(report["missing_authentication"]), 1)
        self.assertIn("cannot statically audit HTTP methods", report["missing_authentication"][0])

    def test_empty_api_route_methods_fail_closed(self):
        source = '''
@app.api_route("/private", methods=[])
def private():
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 0)
        self.assertIn("api_route methods cannot be empty", report["missing_authentication"][0])

    def test_nonliteral_api_route_method_entry_fails_closed(self):
        source = '''
METHOD = "POST"
@app.api_route("/private", methods=["GET", METHOD])
def private():
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 0)
        self.assertIn("only literal strings", report["missing_authentication"][0])

    def test_dynamic_route_path_fails_closed(self):
        source = '''
PATH = "/private"
@app.get(PATH)
def private():
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 0)
        self.assertIn("route path must be a literal string", report["missing_authentication"][0])

    def test_keyword_literal_route_path_is_audited(self):
        source = '''
@app.get(path="/private")
def private():
    return None
'''
        report = audit_source(source)
        self.assertEqual(report["route_count"], 1)
        self.assertEqual(report["missing_authentication"], [
            "GET /private (private) in app.py has no Depends(user) authentication"
        ])

    def test_strict_cli_fails_for_an_authentication_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "app.py"
            source.write_text('@app.get("/private")\ndef private():\n    return None\n', encoding="utf-8")
            self.assertEqual(main(["--app", str(source), "--strict"]), 1)


if __name__ == "__main__":
    unittest.main()
