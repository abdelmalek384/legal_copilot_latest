"""Require every FastAPI route to appear in the tenant-isolation review inventory."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTE_DECORATOR = re.compile(
    r"""@app\.(get|post|put|patch|delete|options|head)\(\s*(['"])(.*?)\2""",
    re.IGNORECASE | re.DOTALL,
)


class TenantRouteInventoryCoverageTests(unittest.TestCase):
    def test_every_application_route_is_documented(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        inventory = (ROOT / "docs" / "tenant_isolation_inventory.md").read_text(encoding="utf-8")
        routes = {
            f"{method.upper()} {path}"
            for method, _quote, path in ROUTE_DECORATOR.findall(source)
        }
        missing = sorted(route for route in routes if route not in inventory)
        self.assertFalse(
            missing,
            "Every HTTP route must be explicitly represented in "
            "docs/tenant_isolation_inventory.md before tenant-isolation review is considered complete:\n"
            + "\n".join(f"- {route}" for route in missing),
        )

    def test_inventory_declares_its_scope_limitations(self):
        inventory = (ROOT / "docs" / "tenant_isolation_inventory.md").read_text(encoding="utf-8")
        self.assertIn("not proof that every authorization branch has been tested", inventory)
        self.assertIn("Do not onboard unrelated firms or production confidential client material yet", inventory)


if __name__ == "__main__":
    unittest.main()
