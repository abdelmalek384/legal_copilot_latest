"""Extraction limits are enforced incrementally for PDF and DOCX inputs."""
import hashlib
import io
import unittest
from unittest.mock import patch

import app


class FakePage:
    def __init__(self, text, calls=None):
        self.text = text
        self.calls = calls

    def extract_text(self):
        if self.calls is not None:
            self.calls.append("extracted")
        return self.text


class FakeReader:
    pages = []

    def __init__(self, stream, strict=True):
        self.pages = self.__class__.pages


class DocumentExtractionBudgetTests(unittest.TestCase):
    def test_pdf_extraction_stops_at_text_budget(self):
        calls = []
        FakeReader.pages = [FakePage("X" * 1_000_001, calls), FakePage("must not be extracted", calls)]
        with patch("pypdf.PdfReader", FakeReader):
            with self.assertRaises(app.HTTPException) as caught:
                app.extract("large.pdf", b"fake PDF")
        self.assertEqual(caught.exception.status_code, 413)
        self.assertEqual(calls, ["extracted"])

    def test_pdf_text_at_budget_is_preserved_with_page_marker(self):
        FakeReader.pages = [FakePage("Readable legal text")]
        with patch("pypdf.PdfReader", FakeReader):
            result = app.extract("small.pdf", b"fake PDF")
        self.assertEqual(result, "[[PDF_PAGE:1]]\n\nReadable legal text")

    def test_docx_extraction_stops_at_text_budget(self):
        import docx
        document = docx.Document()
        document.add_paragraph("".join(hashlib.sha256(str(i).encode()).hexdigest() for i in range(30_000)))
        stream = io.BytesIO()
        document.save(stream)
        with self.assertRaises(app.HTTPException) as caught:
            app.extract("large.docx", stream.getvalue())
        self.assertEqual(caught.exception.status_code, 413)

    def test_unsupported_extension_still_rejected(self):
        with self.assertRaises(app.HTTPException) as caught:
            app.extract("case.txt", b"plain text")
        self.assertEqual(caught.exception.status_code, 415)


if __name__ == "__main__":
    unittest.main()
