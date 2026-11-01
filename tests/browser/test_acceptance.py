"""Real Chromium acceptance tests using synthetic disposable firm/corpus data only."""
from __future__ import annotations

import io
import os
import secrets
import socket
import tempfile
import threading
import time
import faulthandler
import unittest
import zipfile
from xml.sax.saxutils import escape
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


def _synthetic_docx_bytes(text: str) -> bytes:
    """Build a minimal valid DOCX containing only synthetic test text."""
    buffer = io.BytesIO()
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:r><w:t xml:space="preserve">'
        + escape(text)
        + '</w:t></w:r></w:p><w:sectPr/></w:body></w:document>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    relationships = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/>'
        '</Relationships>'
    )
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", relationships)
        archive.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


class BrowserAcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Emit Python thread stacks during any long browser stall so CI timeouts are diagnosable.
        faulthandler.dump_traceback_later(90, repeat=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="legal-copilot-browser-")
        cls.temp_path = Path(cls.temp.name)
        cls.port = _free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.original_env = os.environ.copy()
        sensitive_prefixes = (
            "COPILOT_", "LEGAL_", "LLM_", "MFA_", "SMTP_", "EMAIL_",
            "OPENAI_", "ANTHROPIC_", "GEMINI_", "OLLAMA_", "MISTRAL_", "AWS_",
        )
        sensitive_names = {"ADMIN_TOKEN", "BACKUP_KEY", "MFA_ENCRYPTION_KEY", "DATABASE_URL"}
        for key in tuple(os.environ):
            if key.startswith(sensitive_prefixes) or key in sensitive_names:
                os.environ.pop(key, None)
        # Never inherit the temporary unlinked-legacy retrieval escape hatch.
        os.environ.pop("ALLOW_UNLINKED_LEGACY_LAW_SEARCH", None)
        os.environ.update(
            {
                "COPILOT_ENV": "development",
                "COPILOT_CONTROL_DB": str(cls.temp_path / "control.sqlite3"),
                "COPILOT_TENANT_DB_ROOT": str(cls.temp_path / "tenants"),
                "COPILOT_CORPUS_DB": str(cls.temp_path / "corpus.sqlite3"),
                "COPILOT_OBJECT_STORAGE_ROOT": str(cls.temp_path / "objects"),
                "COPILOT_OBJECT_STORAGE_BACKEND": "local",
                "ADMIN_TOKEN": secrets.token_urlsafe(32),
            }
        )

        import app as app_module
        import uvicorn
        from database_runtime import DatabaseRuntime

        cls.app_module = app_module
        cls.runtime = DatabaseRuntime.from_env()
        cls.runtime.initialize()
        firm_a, _ = cls.runtime.provision_firm("Synthetic Acceptance Firm A")
        firm_b, _ = cls.runtime.provision_firm("Synthetic Acceptance Firm B")

        password = secrets.token_urlsafe(32)
        owner_a = cls.runtime.create_initial_firm_owner(
            firm_a, "Synthetic Firm A Owner", "owner-a@example.test", app_module.hash_pw(password)
        )
        owner_b = cls.runtime.create_initial_firm_owner(
            firm_b, "Synthetic Firm B Owner", "owner-b@example.test", app_module.hash_pw(password)
        )
        reviewer_id = cls.runtime.create_global_identity(
            "Synthetic Platform Reviewer", "reviewer@example.test", app_module.hash_pw(password)
        )
        cls.runtime.create_firm_membership(reviewer_id, firm_a, "lawyer")
        control = cls.runtime.control_connection()
        control.execute(
            "INSERT INTO user_platform_roles(user_id,role_name) VALUES(?,?)",
            (reviewer_id, "platform_reviewer"),
        )
        control.commit()

        firm_b_context = cls.runtime.resolve_context(owner_b, firm_b)
        firm_b_db = cls.runtime.firm_connection(firm_b_context)
        cursor = firm_b_db.execute(
            "INSERT INTO cases(id,title,created_by,firm_id) VALUES(777,?,?,?)",
            ("CROSS_FIRM_PRIVATE_SENTINEL_7D3A", owner_b, firm_b),
        )
        firm_b_db.commit()

        corpus = cls.runtime.legal_corpus_connection()
        corpus.execute(
            """INSERT INTO legal_sources(
                   source_id,authority,source_page,collection_permission,commercial_reuse_permission
               ) VALUES(?,?,?,?,?)""",
            (
                "SYNTHETIC-BROWSER-SOURCE-2026",
                "Synthetic Browser Authority",
                "https://example.invalid/synthetic-source",
                "unknown",
                "unknown",
            ),
        )
        corpus.execute(
            """INSERT INTO legal_documents(
                   document_id,source_id,official_title,document_type,practice_area,law_number,law_year
               ) VALUES(?,?,?,?,?,?,?)""",
            (
                "SYNTHETIC-BROWSER-DOC-2026",
                "SYNTHETIC-BROWSER-SOURCE-2026",
                "SYNTHETIC METADATA ONLY INSTRUMENT 2026",
                "law",
                "synthetic_test_only",
                "999",
                2026,
            ),
        )
        corpus.execute(
            """INSERT INTO legal_sources(
                   source_id,authority,source_page,collection_permission,
                   commercial_reuse_permission,permission_evidence
               ) VALUES(?,?,?,?,?,?)""",
            (
                "SYNTHETIC-BROWSER-VERIFIED-SOURCE",
                "Synthetic Verified Fixture Authority",
                "https://example.test/synthetic-verified-source",
                "allowed",
                "allowed",
                "Synthetic-only fixture permission evidence; not a real legal source.",
            ),
        )
        corpus.execute(
            """INSERT INTO legal_documents(
                   document_id,source_id,official_title,document_type,practice_area
               ) VALUES(?,?,?,?,?)""",
            (
                "SYNTHETIC-BROWSER-VERIFIED-DOC",
                "SYNTHETIC-BROWSER-VERIFIED-SOURCE",
                "SYNTHETIC TEST FIXTURE - NOT LAW",
                "statute",
                "synthetic_test_only",
            ),
        )
        version_id = corpus.execute(
            """INSERT INTO legal_document_versions(
                   document_id,version_label,source_url,publication_date,effective_date,
                   legal_status,review_status,authenticity_verified,status_verified,
                   amendment_history_verified,permission_evidence,original_sha256
               ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "SYNTHETIC-BROWSER-VERIFIED-DOC",
                "synthetic-fixture-current",
                "https://example.test/synthetic-verified-source/version",
                "2020-01-01",
                "2020-01-01",
                "in_force",
                "verified",
                1,
                1,
                1,
                "Synthetic-only fixture permission evidence.",
                "a" * 64,
            ),
        ).lastrowid
        for review_type in (
            "source_authenticity",
            "extraction_quality",
            "legal_status",
            "amendment_history",
            "licensing",
            "lawyer_approval",
        ):
            notes = "Synthetic fixture only; not a legal review."
            if review_type == "lawyer_approval":
                notes = (
                    f"[qualified_egyptian_counsel_attested:user_id={reviewer_id}] "
                    "synthetic fixture marker only; no real legal review occurred."
                )
            corpus.execute(
                """INSERT INTO legal_review_events(
                       version_id,reviewer,review_type,outcome,notes,evidence_url
                   ) VALUES(?,?,?,?,?,?)""",
                (
                    version_id,
                    "Synthetic fixture reviewer",
                    review_type,
                    "pass",
                    notes,
                    "https://example.test/synthetic-review-evidence",
                ),
            )
        verified_text = (
            "CORPUS_ONLY_VERIFIED_SENTINEL_2C77 "
            "Synthetic verified fixture deadline example for browser scope tests."
        )
        corpus.execute(
            """INSERT INTO chunks(
                   ref,article,page,text,norm,document_version_id,in_force,as_of,source,verified
               ) VALUES(?,?,?,?,?,?,?,?,?,1)""",
            (
                "Synthetic fixture Article 12",
                "12",
                "17",
                verified_text,
                app_module.norm(verified_text),
                version_id,
                1,
                "2020-01-01",
                "SYNTHETIC-BROWSER-VERIFIED-SOURCE",
            ),
        )
        corpus.commit()
        app_module.LLM = lambda _prompt: None

        cls.state = {
            "owner_a_email": "owner-a@example.test",
            "owner_b_email": "owner-b@example.test",
            "reviewer_email": "reviewer@example.test",
            "password": password,
            "firm_a_id": firm_a,
            "firm_b_id": firm_b,
            "firm_b_case_id": int(cursor.lastrowid),
        }
        app_module._database_runtime = cls.runtime
        cls.server = uvicorn.Server(
            uvicorn.Config(app_module.app, host="127.0.0.1", port=cls.port, log_level="warning")
        )
        cls.server_thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.server_thread.start()
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline and not cls.server.started:
            if not cls.server_thread.is_alive():
                raise RuntimeError("Synthetic in-process application server exited during startup.")
            time.sleep(0.1)
        if not cls.server.started:
            raise RuntimeError("Synthetic in-process application server did not become ready.")

        # Verify the HTTP listener and root route independently before Chromium starts.
        # This separates server/startup failures from browser navigation failures.
        try:
            with urllib.request.urlopen(cls.base_url + "/", timeout=5) as response:
                html = response.read(2 * 1024 * 1024 + 1)
                if response.status != 200 or len(html) > 2 * 1024 * 1024 or b"Legal Copilot" not in html:
                    raise RuntimeError(
                        "Synthetic browser server root probe failed: "
                        f"status={response.status}, bytes={len(html)}"
                    )
        except (OSError, urllib.error.URLError) as exc:
            raise RuntimeError(
                f"Synthetic browser server did not answer on {cls.base_url}: {exc}"
            ) from exc

        cls.playwright = sync_playwright().start()
        cls.browser: Browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls) -> None:
        faulthandler.cancel_dump_traceback_later()
        if hasattr(cls, "browser"):
            cls.browser.close()
        if hasattr(cls, "playwright"):
            cls.playwright.stop()
        if hasattr(cls, "server"):
            cls.server.should_exit = True
        if hasattr(cls, "server_thread"):
            cls.server_thread.join(timeout=10)
        if hasattr(cls, "app_module"):
            cls.app_module._database_runtime = None
        if hasattr(cls, "runtime"):
            cls.runtime.close_current_thread()
        if hasattr(cls, "temp"):
            cls.temp.cleanup()
        if hasattr(cls, "original_env"):
            os.environ.clear()
            os.environ.update(cls.original_env)

    def setUp(self) -> None:
        self.context: BrowserContext = self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            accept_downloads=True,
        )
        self.page: Page = self.context.new_page()
        # Keep a broken local route or selector from consuming the entire CI budget.
        self.page.set_default_timeout(8000)
        self.page.set_default_navigation_timeout(8000)
        self.browser_errors: list[str] = []
        self.network_errors: list[str] = []
        self.page.on("pageerror", lambda error: self.browser_errors.append(str(error)))
        self.page.on(
            "requestfailed",
            lambda request: self.network_errors.append(
                f"{request.method} {request.url}: {request.failure}"
            ),
        )

    def tearDown(self) -> None:
        result = getattr(getattr(self, "_outcome", None), "result", None)
        failed = bool(result and any(test is self for test, _ in result.errors + result.failures))
        if failed and not self.page.is_closed():
            try:
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                safe_name = self.id().rsplit(".", 1)[-1]
                self.page.screenshot(
                    path=str(ARTIFACT_DIR / f"{safe_name}.png"),
                    full_page=True,
                    timeout=5000,
                )
            except Exception:
                # Preserve the original assertion/navigation error if screenshot capture fails.
                pass
        self.context.close()

    def stage(self, label: str) -> None:
        print(f"BROWSER_STAGE {self.id()} {label}", flush=True)

    def login(self, email: str) -> None:
        self.stage("login.goto.start")
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        self.stage("login.goto.done")
        email_input = self.page.locator('input[type="email"]')
        try:
            email_input.wait_for(state="visible", timeout=10000)
            self.stage("login.email.visible")
        except PlaywrightTimeoutError as exc:
            try:
                body = self.page.locator("body").inner_text(timeout=1500)[:2000]
            except Exception as body_exc:
                body = f"<body unavailable: {type(body_exc).__name__}: {body_exc}>"
            raise AssertionError(
                "Login UI did not render. URL=%s title=%s body=%s "
                "browser_errors=%s network_errors=%s server_thread_alive=%s"
                % (
                    self.page.url,
                    self.page.title(),
                    body,
                    self.browser_errors,
                    self.network_errors,
                    self.server_thread.is_alive(),
                )
            ) from exc
        self.stage("login.fill.start")
        email_input.fill(email)
        self.page.locator('input[type="password"]').fill(self.state["password"])
        self.stage("login.submit.start")
        self.page.locator('button[type="submit"]').click()
        self.stage("login.submit.done")
        self.page.locator("#side").wait_for(state="visible", timeout=15000)
        self.stage("login.complete")

    def csrf_headers(self) -> dict[str, str]:
        cookies = {item["name"]: item["value"] for item in self.context.cookies()}
        return {"X-CSRF-Token": cookies.get("lc_csrf", "")}

    def read_clipboard(self) -> str:
        # Clipboard APIs return promises; explicitly bound them so browser CI
        # cannot hang forever if a headless runner denies or stalls clipboard access.
        return self.page.evaluate(
            """async () => Promise.race([
                navigator.clipboard.readText(),
                new Promise((_, reject) => setTimeout(
                    () => reject(new Error("clipboard read timed out")), 3000
                ))
            ])"""
        )

    def test_corpus_coverage_requires_platform_reviewer_and_drilldown_is_metadata_only(self) -> None:
        self.login(self.state["owner_a_email"])
        denied = self.page.request.get(self.base_url + "/legal-review/coverage", timeout=8000)
        self.assertEqual(denied.status, 403)
        self.assertNotIn("SYNTHETIC METADATA ONLY", denied.text())

        self.context.clear_cookies()
        self.login(self.state["reviewer_email"])
        self.page.get_by_role("button", name="تغطية المجموعة القانونية").click()
        self.page.get_by_role("heading", name="تغطية المجموعة القانونية").wait_for(timeout=10000)
        self.page.get_by_role("heading", name="فهرس الأدوات المرشحة").wait_for(timeout=10000)
        dashboard_text = self.page.locator("body").inner_text()
        self.assertIn("عدد الأدوات في فهرس التخطيط", dashboard_text)
        self.assertIn("سجلات بها مشكلات تحقق", dashboard_text)
        self.assertIn("هذا المقام يصف سجل التخطيط فقط", dashboard_text)

        self.page.get_by_text("الأدوات القانونية المسجلة", exact=True).click()
        search = self.page.get_by_placeholder("ابحث بالعنوان أو المعرف أو الجهة")
        search.fill("SYNTHETIC METADATA ONLY INSTRUMENT 2026")
        self.page.get_by_role("button", name="بحث", exact=True).click()
        self.page.get_by_text("SYNTHETIC METADATA ONLY INSTRUMENT 2026").wait_for(timeout=10000)
        body = self.page.locator("body").inner_text()
        self.assertIn("Shared legal-registry metadata only", body)
        self.assertNotIn("CROSS_FIRM_PRIVATE_SENTINEL_7D3A", body)
        search.fill("NO_MATCHING_SYNTHETIC_CATALOG_ENTRY_2026")
        self.page.get_by_role("button", name="بحث", exact=True).click()
        self.page.get_by_text("لا توجد سجلات مطابقة.").wait_for(timeout=10000)

    def test_research_scopes_keep_metadata_and_firm_documents_separate(self) -> None:
        self.login(self.state["owner_a_email"])
        self.context.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.base_url)
        case_response = self.page.request.post(
            self.base_url + "/cases",
            data={"title": "SYNTHETIC MATTER ONLY FIXTURE"},
            headers=self.csrf_headers(),
            timeout=8000,
        )
        self.assertEqual(case_response.status, 200, case_response.text())
        case_id = case_response.json()["id"]

        sentinel = "FIRM_DOCUMENT_ONLY_SENTINEL_4B91"
        synthetic_docx = _synthetic_docx_bytes(
            sentinel + " Synthetic matter-only passage for browser scope testing."
        )
        upload = self.page.request.post(
            self.base_url + f"/cases/{case_id}/upload",
            multipart={
                "file": {
                    "name": "synthetic-matter-fixture.docx",
                    "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "buffer": synthetic_docx,
                }
            },
            headers=self.csrf_headers(),
            timeout=8000,
        )
        self.assertEqual(upload.status, 200, upload.text())

        self.page.locator("#side").get_by_role("button", name="البحث القانوني").click()
        scope = self.page.locator(".research-controls select").nth(0)
        matter = self.page.locator(".research-controls select").nth(1)
        composer = self.page.locator(".research-composer textarea")

        scope.select_option("firm_documents")
        self.page.locator(".research-composer button").click()
        self.assertIn("اختر ملف قضية", self.page.locator("body").inner_text())

        matter.select_option(str(case_id))
        composer.fill(sentinel)
        self.page.locator(".research-composer button").click()
        self.page.get_by_text("مستند مكتب غير متحقق", exact=False).wait_for(timeout=20000)
        body = self.page.locator("body").inner_text()
        self.assertIn(sentinel, body)
        self.assertIn("مستند مكتب غير متحقق", body)

        self.page.get_by_role("button", name="نسخ الاستشهاد").click()
        copied_citation = self.read_clipboard()
        self.assertTrue(copied_citation.strip())

        self.page.get_by_role("button", name="نسخ المقطع الحرفي").click()
        copied_passage = self.read_clipboard()
        self.assertIn(sentinel, copied_passage)

        with self.page.expect_download() as download_info:
            self.page.get_by_role("button", name="تصدير مذكرة بحث").click()
        download_path = download_info.value.path()
        self.assertIsNotNone(download_path)
        memo_text = Path(download_path).read_text(encoding="utf-8")
        self.assertIn(sentinel, memo_text)

        self.page.get_by_role("button", name="حفظ إلى ملف قضية").click()
        self.page.get_by_text("تم حفظ مذكرة البحث في ملاحظات القضية", exact=False).wait_for(timeout=10000)
        saved_case = self.page.request.get(self.base_url + f"/cases/{case_id}", timeout=8000)
        self.assertEqual(saved_case.status, 200, saved_case.text())
        self.assertTrue(any(sentinel in note["text"] for note in saved_case.json()["notes"]))

        scope.select_option("verified_corpus")
        # Start a fresh conversation so prior firm-matter messages are not part of this UI assertion.
        self.page.locator(".research-list-head").get_by_role("button", name="محادثة جديدة").click()
        self.page.locator(".research-thread .research-empty").wait_for(timeout=10000)
        composer.fill(sentinel)
        self.page.locator(".research-composer button").click()
        self.page.get_by_text("لم يُعثر على نص قانوني متحقق ذي صلة", exact=False).wait_for(timeout=20000)
        latest_assistant = self.page.locator(".research-thread .research-message.assistant").last.inner_text()
        self.assertNotIn(sentinel, latest_assistant)

        scope.select_option("verified_corpus")
        composer.fill("synthetic verified fixture deadline example")
        self.page.locator(".research-composer button").click()
        self.page.get_by_text("CORPUS_ONLY_VERIFIED_SENTINEL_2C77").wait_for(timeout=12000)
        candidate_body = self.page.locator(".research-thread").inner_text()
        # The fixture uses example.test and has no central permission-register
        # record, so it must remain under review rather than become verified.
        self.assertIn("قيد المراجعة", candidate_body)
        self.assertIn("لا تعتبره نصاً سارياً متحققاً", candidate_body)
        self.assertNotIn("نص ساري متحقق منه", candidate_body)
        self.assertIn("المادة 12", candidate_body)
        self.assertIn("الصفحة 17", candidate_body)
        candidate_assistant = self.page.locator(".research-thread .research-message.assistant").last.inner_text()
        self.assertNotIn("FIRM_DOCUMENT_ONLY_SENTINEL_4B91", candidate_assistant)

        scope.select_option("metadata_only")
        composer.fill("SYNTHETIC METADATA ONLY INSTRUMENT 2026")
        self.page.locator(".research-composer button").click()
        self.page.get_by_text("SYNTHETIC METADATA ONLY INSTRUMENT 2026").wait_for(timeout=10000)
        discovery = self.page.locator(".research-thread").inner_text()
        self.assertIn("لم يُسترجع أي نص قانوني", discovery)
        self.assertNotIn(sentinel, discovery)

    def test_z_research_inspector_scope_and_empty_state_are_keyboard_operable(self) -> None:
        self.login(self.state["owner_a_email"])
        research_nav = self.page.locator("#side").get_by_role("button", name="البحث القانوني")
        research_nav.focus()
        research_nav.press("Enter")
        self.page.locator(".research-controls select").nth(0).wait_for(state="visible", timeout=10000)

        scope = self.page.locator(".research-controls select").nth(0)
        matter = self.page.locator(".research-controls select").nth(1)
        composer = self.page.locator(".research-composer textarea")
        send = self.page.locator(".research-composer button")

        # Verify the actual Tab sequence from the scope selector through
        # matter selection, query entry, and submission; no pointer interaction.
        scope.focus()
        self.assertTrue(scope.evaluate("(el) => document.activeElement === el"))
        self.page.keyboard.press("Tab")
        self.assertTrue(matter.evaluate("(el) => document.activeElement === el"))
        # The conversation sidebar contains additional legitimate tab stops
        # between the scope controls and composer. Verify they do not trap or
        # skip keyboard focus rather than assuming an artificially short path.
        composer_reached = False
        focusable_count = self.page.locator(
            "button:not([disabled]), a[href], select:not([disabled]), "
            "textarea:not([disabled]), input:not([disabled]), "
            "[tabindex]:not([tabindex='-1'])"
        ).count()
        # The shared synthetic fixture accumulates research-conversation
        # controls across earlier browser cases. Bound traversal by the actual
        # number of focusable elements rather than assuming a fixed list size.
        for _ in range(focusable_count + 2):
            self.page.keyboard.press("Tab")
            if composer.evaluate("(el) => document.activeElement === el"):
                composer_reached = True
                break
        self.assertTrue(composer_reached, "query composer was not reachable by Tab")
        self.page.keyboard.press("Tab")
        self.assertTrue(send.evaluate("(el) => document.activeElement === el"))

        scope.select_option("metadata_only")
        composer.focus()
        self.page.keyboard.type("keyboard-only-no-source-query-xyz-2026")
        self.page.keyboard.press("Tab")
        self.assertTrue(send.evaluate("(el) => document.activeElement === el"))
        self.page.keyboard.press("Enter")
        self.page.get_by_text("لم يُعثر على بيانات وصفية مطابقة", exact=False).wait_for(timeout=10000)
        self.assertIn(
            "بيانات وصفية فقط",
            self.page.locator(".research-thread").inner_text(),
        )

    def test_cross_firm_case_identifier_does_not_reveal_other_firm_sentinel(self) -> None:
        self.login(self.state["owner_a_email"])
        response = self.page.request.get(
            self.base_url + f"/cases/{self.state['firm_b_case_id']}", timeout=8000
        )
        self.assertIn(response.status, (403, 404))
        self.assertNotIn("CROSS_FIRM_PRIVATE_SENTINEL_7D3A", response.text())

    def test_expired_session_returns_to_login(self) -> None:
        self.login(self.state["owner_a_email"])
        self.context.clear_cookies()
        self.page.reload(wait_until="domcontentloaded")
        self.page.locator('input[type="email"]').wait_for(state="visible", timeout=15000)

    def test_corpus_coverage_exposes_loading_and_error_states(self) -> None:
        self.login(self.state["reviewer_email"])
        self.page.evaluate(
            """() => {
                const originalFetch = window.fetch.bind(window);
                window.fetch = (input, init) => {
                    if (String(input) === '/legal-review/coverage') {
                        return new Promise(resolve => {
                            window.__resolveCoverage = () => resolve(new Response(
                                JSON.stringify({detail: 'synthetic fixture failure'}),
                                {status: 503, headers: {'content-type': 'application/json'}}
                            ));
                        });
                    }
                    return originalFetch(input, init);
                };
            }"""
        )
        self.page.get_by_role("button", name="تغطية المجموعة القانونية").click()
        self.page.get_by_text("جارٍ تحميل المؤشرات…").wait_for(timeout=10000)
        self.page.evaluate("() => window.__resolveCoverage()")
        self.page.get_by_text("تعذر تحميل المؤشرات. أعد المحاولة.").wait_for(timeout=10000)

    def test_arabic_rtl_and_english_ltr_have_no_mobile_horizontal_overflow(self) -> None:
        self.stage("rtl.login.start")
        self.login(self.state["reviewer_email"])
        self.stage("rtl.login.done")
        self.page.get_by_role("button", name="تغطية المجموعة القانونية").click()
        self.stage("rtl.coverage.click.done")
        self.page.get_by_role("heading", name="تغطية المجموعة القانونية").wait_for(timeout=10000)
        self.stage("rtl.coverage.visible")

        for width, height in ((1440, 900), (375, 812)):
            self.stage(f"rtl.viewport.{width}.start")
            self.page.set_viewport_size({"width": width, "height": height})
            self.stage(f"rtl.viewport.{width}.done")
            self.page.wait_for_function(
                "() => document.documentElement.scrollWidth <= window.innerWidth",
                timeout=8000,
            )
            self.stage(f"rtl.overflow-check.{width}.done")

        self.page.locator("[data-lang-switch='1']").click()
        self.stage("ltr.switch.click.done")
        self.page.get_by_text("Corpus Coverage & Provenance").wait_for(timeout=10000)
        self.page.get_by_role("heading", name="Candidate instrument inventory").wait_for(timeout=10000)
        self.page.get_by_text("This denominator describes the planning inventory only", exact=False).wait_for(timeout=10000)
        self.page.wait_for_function(
            "() => document.documentElement.dir === 'ltr'",
            timeout=8000,
        )
        self.stage("ltr.direction.done")
        for width, height in ((1440, 900), (375, 812)):
            self.stage(f"ltr.viewport.{width}.start")
            self.page.set_viewport_size({"width": width, "height": height})
            self.stage(f"ltr.viewport.{width}.done")
            self.page.wait_for_function(
                "() => document.documentElement.scrollWidth <= window.innerWidth",
                timeout=8000,
            )
            self.stage(f"ltr.overflow-check.{width}.done")

        self.page.keyboard.press("Tab")
        self.page.wait_for_function(
            "() => !!document.activeElement && document.activeElement !== document.body",
            timeout=8000,
        )
        self.stage("keyboard.focus.done")


if __name__ == "__main__":
    unittest.main(verbosity=2)
