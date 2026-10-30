"""Require every registered FastAPI route to appear in the tenant-isolation review inventory."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import app  # noqa: E402


class TenantRouteInventoryCoverageTests(unittest.TestCase):
    def test_every_registered_application_route_is_documented(self):
        inventory = (ROOT / "docs" / "tenant_isolation_inventory.md").read_text(encoding="utf-8")
        routes = set()
        for route in app.app.routes:
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", None) or set()
            if not path or path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
                continue
            for method in methods - {"HEAD", "OPTIONS"}:
                routes.add(f"{method} {path}")
        missing = sorted(route for route in routes if route not in inventory)
        self.assertFalse(
            missing,
            "Every registered HTTP route must be explicitly represented in "
            "docs/tenant_isolation_inventory.md before tenant-isolation review is considered complete:\n"
            + "\n".join(f"- {route}" for route in missing),
        )

    def test_every_non_public_route_requires_authenticated_user_dependency(self):
        # These public routes are intentionally token-bound or return only a
        # generic response: credential entry, invitation acceptance, and password
        # recovery. Firm administration and acceptance by an existing identity still
        # require app.user (including CSRF/session checks).
        public_routes = {
            ("GET", "/"), ("GET", "/manifest.webmanifest"),
            ("GET", "/service-worker.js"), ("GET", "/offline.html"),
            ("GET", "/app-icon.svg"), ("POST", "/login"),
            ("GET", "/invite/accept"), ("GET", "/account/recovery"),
            ("POST", "/invitations/accept/new"),
            ("POST", "/account/recovery/request"),
            ("POST", "/account/recovery/consume"),
        }

        def has_user_dependency(dependant):
            if getattr(dependant, "call", None) is app.user:
                return True
            return any(has_user_dependency(child) for child in getattr(dependant, "dependencies", ()))

        unprotected = []
        for route in app.app.routes:
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", None) or set()
            dependant = getattr(route, "dependant", None)
            if not path or dependant is None or path in {"/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
                continue
            for method in methods - {"HEAD", "OPTIONS"}:
                if (method, path) not in public_routes and not has_user_dependency(dependant):
                    unprotected.append(f"{method} {path}")
        self.assertFalse(
            unprotected,
            "New routes must authenticate through app.user or be explicitly reviewed as public:\\n"
            + "\\n".join(sorted(unprotected)),
        )

    def test_inventory_declares_its_scope_limitations(self):
        inventory = (ROOT / "docs" / "tenant_isolation_inventory.md").read_text(encoding="utf-8")
        self.assertIn("not proof that every authorization branch has been tested", inventory)
        self.assertIn("Do not onboard unrelated firms or production confidential client material yet", inventory)


if __name__ == "__main__":
    unittest.main()
