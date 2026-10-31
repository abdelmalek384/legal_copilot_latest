"""Real Chromium acceptance tests using synthetic disposable firm/corpus data only."""
from __future__ import annotations

import json
import os
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts" / "browser"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class BrowserAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-browser-")
        cls.temp_path = Path(cls.temp.name)
        cls.port = _free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        env = os.environ.copy()
        env.update(
            {
                "COPILOT_ENV": "development",
                "COPILOT_CONTROL_DB": str(cls.temp_path / "control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": str(cls.temp_path / "tenants"),
                "COPILOT_CORPUS_DB": str(cls.temp_path / "corpus.sqlite3"),
                "COPILOT_OBJECT_STORAGE_ROOT": str(cls.temp_path / "objects"),
                "COPILOT_OBJECT_STORAGE_BACKEND": "local",
                "ADMIN_TOKEN": secrets.token_urlsafe(32),
                "BROWSER_FIXTURE_PORT": str(cls.port),
            }
        )
        env.pop("COPILOT_DB", None)
        env.pop("LLM_FIRM_DATA_PROCESSING_APPROVED", None)
        cls.server = subprocess.Popen(
            [sys.executable, "-m", "tests.browser.fixture_server"],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        cls.state_ready = threading.Event()

        def read_fixture_state() -> None:
            line = cls.server.stdout.readline()
            prefix = "BROWSER_FIXTURE_STATE="
            if line.startswith(prefix):
                cls.state = json.loads(line[len(prefix):])
                cls.state_ready.set()

        cls.state_reader = threading.Thread(target=read_fixture_state, daemon=True)
        cls.state_reader.start()
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline and not cls.state_ready.wait(0.1):
            if cls.server.poll() is not None:
                raise RuntimeError("Synthetic fixture server exited before publishing fixture state.")
        if not cls.state_ready.is_set():
            raise RuntimeError("Synthetic fixture server did not publish fixture state.")

        deadline = time.monotonic() + 45
        last_error = None
        while time.monotonic() < deadline:
            if cls.server.poll() is not None:
                raise RuntimeError("Synthetic fixture server exited before becoming ready.")
            try:
                with urllib.request.urlopen(cls.base_url, timeout=2) as response:
                    if response.status == 200:
                        break
            except (OSError, urllib.error.URLError) as exc:
                last_error = exc
                time.sleep(0.25)
        else:
            raise RuntimeError(f"Synthetic fixture server did not become ready: {last_error}")
        cls.playwright = sync_playwright().start()
        cls.browser: Browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "browser"):
            cls.browser.close()
        if hasattr(cls, "playwright"):
            cls.playwright.stop()
        if hasattr(cls, "server") and cls.server.poll() is None:
            cls.server.terminate()
            try:
                cls.server.wait(timeout=8)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait(timeout=5)
        if hasattr(cls, "temp"):
            cls.temp.cleanup()

    def setUp(self) -> None:
        self.context: BrowserContext = self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            accept_downloads=True,
        )
        self.page: Page = self.context.new_page()
        self.browser_errors: list[str] = []
        self.page.on("pageerror", lambda error: self.browser_errors.append(str(error)))

    def tearDown(self) -> None:
        result = getattr(getattr(self, "_outcome", None), "result", None)
        failed = bool(result and any(test is self for test, _ in result.errors + result.failures))
        if failed:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            safe_name = self.id().rsplit(".", 1)[-1]
            self.page.screenshot(
                path=str(ARTIFACT_DIR / f"{safe_name}.png"),
                full_page=True,
            )
        self.context.close()

    def login(self, email: str) -> None:
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        email_input = self.page.locator('input[type="email"]')
        try:
            email_input.wait_for(state="visible", timeout=15000)
        except PlaywrightTimeoutError as exc:
            raise AssertionError(
                "Login UI did not render. URL=%s body=%s browser_errors=%s"
                % (self.page.url, self.page.locator("body").inner_text()[:2000], self.browser_errors)
            ) from exc
        email_input.fill(email)
        self.page.locator('input[type="password"]').fill(self.state["password"])
        self.page.locator('button[type="submit"]').click()
        self.page.locator("#side").wait_for(state="visible", timeout=15000)

    def csrf_headers(self) -> dict[str, str]:
        cookies = {item["name"]: item["value"] for item in self.context.cookies()}
        return {"X-CSRF-Token": cookies.get("lc_csrf", "")}

    def test_corpus_coverage_requires_platform_reviewer_and_drilldown_is_metadata_only(self) -> None:
        self.login(self.state["owner_a_email"])
        denied = self.page.request.get(self.base_url + "/legal-review/coverage")
        self.assertEqual(denied.status, 403)
        self.assertNotIn("SYNTHETIC METADATA ONLY", denied.text())

        self.context.clear_cookies()
        self.login(self.state["reviewer_email"])
        self.page.get_by_role("button", name="تغطية المجموعة القانونية").click()
        self.page.get_by_text("تغطية المجموعة القانونية").wait_for(timeout=10000)

        self.page.get_by_text("الأدوات القانونية المسجلة", exact=True).click()
        search = self.page.get_by_placeholder("ابحث بالعنوان أو المعرف أو الجهة")
        search.fill("SYNTHETIC METADATA ONLY INSTRUMENT 2026")
        self.page.get_by_role("button", name="بحث").click()
        self.page.get_by_text("SYNTHETIC METADATA ONLY INSTRUMENT 2026").wait_for(timeout=10000)
        body = self.page.locator("body").inner_text()
        self.assertIn("Shared legal-registry metadata only", body)
        self.assertNotIn("CROSS_FIRM_PRIVATE_SENTINEL_7D3A", body)

    def test_research_scopes_keep_metadata_and_firm_documents_separate(self) -> None:
        self.login(self.state["owner_a_email"])
        case_response = self.page.request.post(
            self.base_url + "/cases",
            data={"title": "SYNTHETIC MATTER ONLY FIXTURE"},
            headers=self.csrf_headers(),
        )
        self.assertEqual(case_response.status, 200, case_response.text())
        case_id = case_response.json()["id"]

        sentinel = "FIRM_DOCUMENT_ONLY_SENTINEL_4B91"
        upload = self.page.request.post(
            self.base_url + f"/cases/{case_id}/upload",
            multipart={
                "file": {
                    "name": "synthetic-matter-fixture.txt",
                    "mimeType": "text/plain",
                    "buffer": (sentinel + " Synthetic matter-only passage for browser scope testing.").encode(),
                }
            },
            headers=self.csrf_headers(),
        )
        self.assertEqual(upload.status, 200, upload.text())

        self.page.get_by_role("button", name="البحث القانوني").click()
        scope = self.page.locator(".research-controls select").nth(0)
        matter = self.page.locator(".research-controls select").nth(1)
        composer = self.page.locator(".research-composer textarea")

        scope.select_option("firm_documents")
        self.page.locator(".research-composer button").click()
        self.assertIn("اختر ملف قضية", self.page.locator("body").inner_text())

        matter.select_option(str(case_id))
        composer.fill(sentinel)
        self.page.locator(".research-composer button").click()
        self.page.get_by_text(sentinel, exact=False).wait_for(timeout=12000)
        self.assertIn(sentinel, self.page.locator("body").inner_text())

        scope.select_option("verified_corpus")
        composer.fill(sentinel)
        self.page.locator(".research-composer button").click()
        self.page.get_by_text("لم يُعثر على نص قانوني متحقق ذي صلة", exact=False).wait_for(timeout=12000)
        self.assertNotIn(sentinel, self.page.locator(".research-thread").inner_text())

        scope.select_option("metadata_only")
        composer.fill("SYNTHETIC METADATA ONLY INSTRUMENT 2026")
        self.page.locator(".research-composer button").click()
        self.page.get_by_text("SYNTHETIC METADATA ONLY INSTRUMENT 2026").wait_for(timeout=10000)
        discovery = self.page.locator(".research-thread").inner_text()
        self.assertIn("لم يُسترجع أي نص قانوني", discovery)
        self.assertNotIn(sentinel, discovery)

    def test_cross_firm_case_identifier_does_not_reveal_other_firm_sentinel(self) -> None:
        self.login(self.state["owner_a_email"])
        response = self.page.request.get(
            self.base_url + f"/cases/{self.state['firm_b_case_id']}"
        )
        self.assertIn(response.status, (403, 404))
        self.assertNotIn("CROSS_FIRM_PRIVATE_SENTINEL_7D3A", response.text())

    def test_arabic_rtl_and_english_ltr_have_no_mobile_horizontal_overflow(self) -> None:
        self.login(self.state["reviewer_email"])
        self.page.get_by_role("button", name="تغطية المجموعة القانونية").click()
        self.page.get_by_text("تغطية المجموعة القانونية").wait_for(timeout=10000)

        for width, height in ((1440, 900), (375, 812)):
            self.page.set_viewport_size({"width": width, "height": height})
            no_overflow = self.page.evaluate(
                "() => document.documentElement.scrollWidth <= window.innerWidth"
            )
            self.assertTrue(no_overflow, f"Arabic RTL page overflow at viewport {width}x{height}")

        self.page.locator("[data-lang-switch='1']").click()
        self.page.get_by_text("Corpus Coverage & Provenance").wait_for(timeout=10000)
        direction = self.page.evaluate("() => document.documentElement.dir")
        self.assertEqual(direction, "ltr")
        for width, height in ((1440, 900), (375, 812)):
            self.page.set_viewport_size({"width": width, "height": height})
            no_overflow = self.page.evaluate(
                "() => document.documentElement.scrollWidth <= window.innerWidth"
            )
            self.assertTrue(no_overflow, f"English LTR page overflow at viewport {width}x{height}")

        self.page.keyboard.press("Tab")
        focused = self.page.evaluate(
            "() => !!document.activeElement && document.activeElement !== document.body"
        )
        self.assertTrue(focused, "Keyboard navigation did not move focus to an interactive control")


if __name__ == "__main__":
    unittest.main(verbosity=2)
