import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.record_manual_capture import main  # noqa: E402

TEXT = "مادة (1)\nنص تجريبي للمادة الأولى.\n\nمادة (2)\nنص تجريبي للمادة الثانية.\n" + ("وصف إضافي لاستيفاء الحد الأدنى للطول. " * 12)
URL = "https://example.gov.eg/law/14"


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class RecordManualCaptureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.txt = self.dir / "law.txt"
        self.txt.write_text(TEXT, encoding="utf-8")
        self.out = self.dir / "corpus"

    def tearDown(self):
        self.tmp.cleanup()

    def base(self, **over):
        args = {"--file": str(self.txt), "--document-id": "EG-LABOUR-14-2025", "--source-url": URL,
                "--captured-by": "Test Person", "--out": str(self.out), "--retrieved-on": "2026-10-20"}
        args.update(over)
        flat = []
        for k, v in args.items():
            flat += [k, v]
        return flat

    def test_records_provenance_and_marks_nothing_verified(self):
        code, stdout, stderr = run(*self.base())
        self.assertEqual(code, 0, stderr)
        meta = json.loads((self.out / "metadata" / "EG-LABOUR-14-2025.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["collection_mode"], "manual_capture")
        self.assertEqual(meta["captured_by"], "Test Person")
        self.assertEqual(meta["source_url"], URL)
        self.assertFalse(meta["legal_authenticity_verified"])
        self.assertFalse(meta["current_legal_status_verified"])
        self.assertFalse(meta["commercial_reuse_permission_verified"])
        self.assertEqual(meta["collection_permission"], "not_established_manual_capture")
        self.assertTrue((self.out / meta["original_path"]).exists())
        queue = [json.loads(l) for l in (self.out / "review_queue.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(queue[-1]["review_status"], "pending_human_review")
        self.assertTrue(any("permission" in r for r in queue[-1]["review_reasons"]))
        result, _ = json.JSONDecoder().raw_decode(stdout)
        audit = result["audit"]
        self.assertEqual(audit["audit"]["article_headings_detected"], 2)
        self.assertTrue((self.out / audit["audit_path"]).is_file())
        self.assertTrue((self.out / audit["extracted_text_path"]).is_file())

    def test_hash_matches_file(self):
        import hashlib
        run(*self.base())
        meta = json.loads((self.out / "metadata" / "EG-LABOUR-14-2025.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["sha256"], hashlib.sha256(self.txt.read_bytes()).hexdigest())

    def test_rerun_with_same_file_does_not_duplicate_original(self):
        run(*self.base())
        code, stdout, _ = run(*self.base())
        self.assertEqual(code, 0)
        self.assertIn('"already_recorded_file": true', stdout)
        self.assertEqual(len(list((self.out / "originals" / "EG-LABOUR-14-2025").iterdir())), 1)

    def test_dry_run_writes_nothing(self):
        code, _, _ = run(*self.base(), "--dry-run")
        self.assertEqual(code, 0)
        self.assertFalse(self.out.exists())

    def test_rejects_http_and_credential_urls(self):
        for url in ("http://example.gov.eg/x", "https://user:pw@example.gov.eg/x", "ftp://example.gov.eg/x", "not a url"):
            code, _, _ = run(*self.base(**{"--source-url": url}))
            self.assertEqual(code, 2, url)

    def test_rejects_unsupported_and_fake_files(self):
        exe = self.dir / "a.exe"
        exe.write_bytes(b"MZ....")
        self.assertEqual(run(*self.base(**{"--file": str(exe)}))[0], 2)
        fake = self.dir / "fake.pdf"
        fake.write_bytes(b"this is not a pdf")
        code, _, err = run(*self.base(**{"--file": str(fake)}))
        self.assertEqual(code, 2)
        self.assertIn("signature", err)
        empty = self.dir / "empty.txt"
        empty.write_bytes(b"")
        self.assertEqual(run(*self.base(**{"--file": str(empty)}))[0], 2)

    def test_rejects_non_utf8_text(self):
        bad = self.dir / "bad.txt"
        bad.write_bytes("نص".encode("windows-1256"))
        code, _, err = run(*self.base(**{"--file": str(bad)}))
        self.assertEqual(code, 2)
        self.assertIn("UTF-8", err)

    def test_unknown_document_requires_source_id(self):
        code, _, err = run(*self.base(**{"--document-id": "EG-NOT-IN-CATALOG"}))
        self.assertEqual(code, 2)
        self.assertIn("not in docs/legal_document_candidates.json", err)
        code, _, err = run(*self.base(**{"--document-id": "EG-NOT-IN-CATALOG", "--source-id": "EG-AMIRI-PRESS"}))
        self.assertEqual(code, 0, err)

    def test_rejects_bad_or_future_dates_and_blank_name(self):
        self.assertEqual(run(*self.base(**{"--retrieved-on": "20-10-2026"}))[0], 2)
        self.assertEqual(run(*self.base(**{"--retrieved-on": "2999-01-01"}))[0], 2)
        self.assertEqual(run(*self.base(**{"--captured-by": "   "}))[0], 2)
        self.assertEqual(run(*self.base(**{"--publication-date": "May 3"}))[0], 2)

    def test_html_capture_and_extraction(self):
        html = self.dir / "page.html"
        html.write_text("<html><body><p>مادة (1)</p><p>نص</p></body></html>", encoding="utf-8")
        code, _, err = run(*self.base(**{"--file": str(html)}))
        self.assertEqual(code, 0, err)


if __name__ == "__main__":
    unittest.main()
