"""Regression tests for OCR fallback with structural PDF page markers."""
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import app


class FakePdfPage:
    def __init__(self, number):
        self.number = number
    def get_pixmap(self, dpi, alpha):
        return FakePixmap()


class FakePixmap:
    def tobytes(self, kind):
        return b"png-bytes"


class FakePdfDoc:
    def __init__(self, count):
        self.pages = [FakePdfPage(i) for i in range(count)]
    def __len__(self):
        return len(self.pages)
    def __iter__(self):
        return iter(self.pages)


class PdfOcrFallbackTests(unittest.TestCase):
    def test_page_markers_do_not_count_as_readable_text(self):
        marker_only = "[[PDF_PAGE:1]]\n\n[[PDF_PAGE:2]]"
        self.assertEqual(app._extracted_text_content(marker_only), "")
        readable = "[[PDF_PAGE:1]]\n\nThis page contains readable legal text."
        self.assertEqual(app._extracted_text_content(readable), "This page contains readable legal text.")

    def test_page_text_parser_preserves_each_page_separately(self):
        text = "[[PDF_PAGE:1]]\n\nReadable page one text is longer than twenty chars.\n\n[[PDF_PAGE:2]]\n\n"
        self.assertEqual(app._pdf_page_texts(text), {
            1: "Readable page one text is longer than twenty chars.",
            2: "",
        })

    def test_ocr_only_missing_pages_and_keep_existing_text(self):
        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(2))
        fake_pytesseract = types.SimpleNamespace(image_to_string=MagicMock(return_value="OCR recovered page two text."))
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }):
            result = app.ocr_pdf_text(
                b"pdf",
                existing_pages={1: "Readable page one text is longer than twenty chars.", 2: ""},
            )
        self.assertIn("[[PDF_PAGE:1]]\n\nReadable page one text is longer than twenty chars.", result)
        self.assertIn("[[PDF_PAGE:2]]\n\nOCR recovered page two text.", result)
        fake_pytesseract.image_to_string.assert_called_once()

    def test_all_scanned_pdf_still_obeys_ocr_page_limit(self):
        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(31))
        fake_pytesseract = types.SimpleNamespace(image_to_string=MagicMock(return_value="ocr text"))
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }):
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf", existing_pages={i: "" for i in range(1, 32)})
        self.assertEqual(caught.exception.status_code, 413)


    def test_ocr_output_obeys_one_megabyte_extraction_budget(self):
        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(1))
        fake_pytesseract = types.SimpleNamespace(
            image_to_string=MagicMock(return_value="X" * 1_000_001)
        )
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }):
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf")
        self.assertEqual(caught.exception.status_code, 413)
        self.assertIn("1 MB", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
