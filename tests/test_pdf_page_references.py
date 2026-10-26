"""PDF and OCR-derived case-file chunks retain page-level citation metadata."""
import sqlite3
import unittest
from unittest.mock import patch

import app


class FakePage:
    def __init__(self, text):
        self._text = text
    def extract_text(self):
        return self._text


class FakeReader:
    def __init__(self, stream, strict=True):
        self.pages = [FakePage("First page paragraph.\n\nAnother paragraph on page one."),
                      FakePage("Second page paragraph.")]


class PageAwareDocumentTests(unittest.TestCase):
    def test_pdf_page_boundaries_flow_into_chunk_metadata(self):
        with patch("pypdf.PdfReader", FakeReader):
            extracted = app.extract("pleading.pdf", b"fake pdf bytes")
        db = sqlite3.connect(":memory:")
        db.execute("""CREATE TABLE chunks(
            id INTEGER PRIMARY KEY, ref TEXT, article TEXT, page TEXT, text TEXT, norm TEXT,
            case_id INT, in_force INT, as_of TEXT, source TEXT, verified INT, document_id INT)""")
        with patch.object(app, "_separate_runtime_enabled", return_value=True):
            count = app.add_doc(db, 12, "pleading.pdf", extracted, document_id=44)
        rows = db.execute("SELECT ref,page,text FROM chunks ORDER BY id").fetchall()
        self.assertEqual(count, 3)
        self.assertEqual([r[1] for r in rows], ["1", "1", "2"])
        self.assertEqual([r[2] for r in rows], [
            "First page paragraph.", "Another paragraph on page one.", "Second page paragraph."
        ])
        self.assertIn("page 1", rows[0][0])
        self.assertIn("page 2", rows[2][0])
        self.assertNotIn("PDF_PAGE", " ".join(r[2] for r in rows))
        db.close()

    def test_non_pdf_documents_keep_unknown_page(self):
        db = sqlite3.connect(":memory:")
        db.execute("""CREATE TABLE chunks(
            id INTEGER PRIMARY KEY, ref TEXT, article TEXT, page TEXT, text TEXT, norm TEXT,
            case_id INT, in_force INT, as_of TEXT, source TEXT, verified INT, document_id INT)""")
        with patch.object(app, "_separate_runtime_enabled", return_value=True):
            app.add_doc(db, 12, "contract.docx", "Paragraph one.\n\nParagraph two.", document_id=45)
        rows = db.execute("SELECT ref,page,text FROM chunks ORDER BY id").fetchall()
        self.assertEqual([r[1] for r in rows], [None, None])
        self.assertIn("paragraph 1", rows[0][0])
        self.assertIn("paragraph 2", rows[1][0])
        db.close()


if __name__ == "__main__":
    unittest.main()
