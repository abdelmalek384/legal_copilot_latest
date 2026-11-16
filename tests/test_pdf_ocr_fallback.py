"""Regression tests for OCR fallback with structural PDF page markers."""
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import app


class FakePdfPage:
    def __init__(self, number):
        self.number = number
        self.rect = types.SimpleNamespace(width=612.0, height=792.0)
    def get_pixmap(self, dpi, alpha):
        return FakePixmap()


class FakePixmap:
    width = 1360
    height = 1760
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

    def test_oversized_page_is_rejected_before_pdf_rasterization(self):
        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(1))
        fake_pytesseract = types.SimpleNamespace(image_to_string=MagicMock(return_value="must not run"))
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }), patch.dict(os.environ, {"OCR_MAX_PIXELS": "1000"}), patch.object(
            FakePdfPage, "get_pixmap", autospec=True
        ) as render_page:
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf")
        self.assertEqual(caught.exception.status_code, 413)
        render_page.assert_not_called()
        fake_pytesseract.image_to_string.assert_not_called()

    def test_ocr_environment_cannot_raise_hard_raster_ceilings(self):
        fake_pytesseract = types.SimpleNamespace(
            image_to_string=MagicMock(return_value="must not run")
        )
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image

        for width_points, height_points in (
            (10_000.0, 10.0),
            (5_000.0, 5_000.0),
        ):
            with self.subTest(width=width_points, height=height_points):
                document = FakePdfDoc(1)
                document.pages[0].rect = types.SimpleNamespace(
                    width=width_points, height=height_points
                )
                fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: document)
                with patch.dict(sys.modules, {
                    "pymupdf": fake_pymupdf,
                    "pytesseract": fake_pytesseract,
                    "PIL": fake_pil,
                }), patch.dict(os.environ, {
                    "OCR_MAX_PIXELS": "999999999999",
                    "OCR_MAX_DIMENSION": "999999999999",
                }), patch.object(
                    FakePdfPage, "get_pixmap", autospec=True
                ) as render_page:
                    with self.assertRaises(app.HTTPException) as caught:
                        app.ocr_pdf_text(b"pdf")
                self.assertEqual(caught.exception.status_code, 413)
                self.assertIn("configured OCR raster limit", caught.exception.detail)
                render_page.assert_not_called()

        fake_pytesseract.image_to_string.assert_not_called()

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


    def test_ocr_saturation_fails_closed_without_starting_another_ocr_job(self):
        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(1))
        fake_pytesseract = types.SimpleNamespace(image_to_string=MagicMock(return_value="should not run"))
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image

        class SaturatedSemaphore:
            def acquire(self, timeout=None):
                self.timeout = timeout
                return False

            def release(self):
                raise AssertionError("release must not run when acquire fails")

        semaphore = SaturatedSemaphore()
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }), patch.object(app, "_OCR_SEMAPHORE", semaphore), patch.object(
            FakePdfPage, "get_pixmap", autospec=True
        ) as render_page:
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf")

        self.assertEqual(caught.exception.status_code, 503)
        self.assertEqual(semaphore.timeout, 5)
        render_page.assert_not_called()
        fake_pytesseract.image_to_string.assert_not_called()

    def test_ocr_subprocess_timeout_is_reported_and_releases_capacity(self):
        import subprocess

        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(1))
        image_to_string = MagicMock(side_effect=subprocess.TimeoutExpired("tesseract", 30))
        fake_pytesseract = types.SimpleNamespace(image_to_string=image_to_string)
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image

        class TrackingSemaphore:
            def __init__(self):
                self.releases = 0

            def acquire(self, timeout=None):
                self.timeout = timeout
                return True

            def release(self):
                self.releases += 1

        semaphore = TrackingSemaphore()
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }), patch.object(app, "_OCR_SEMAPHORE", semaphore):
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf")

        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(semaphore.timeout, 5)
        self.assertEqual(semaphore.releases, 1)
        image_to_string.assert_called_once()
        self.assertEqual(image_to_string.call_args.kwargs["timeout"], 30)

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


    def test_oversized_page_dimension_is_rejected_before_pdf_rasterization(self):
        class WidePdfPage(FakePdfPage):
            def __init__(self, number):
                super().__init__(number)
                self.rect = types.SimpleNamespace(width=100_000.0, height=792.0)

        class WidePdfDoc:
            def __len__(self):
                return 1

            def __iter__(self):
                return iter([WidePdfPage(0)])

        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: WidePdfDoc())
        fake_pytesseract = types.SimpleNamespace(image_to_string=MagicMock(return_value="must not run"))
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }), patch.dict(os.environ, {"OCR_MAX_DIMENSION": "1000"}), patch.object(
            WidePdfPage, "get_pixmap", autospec=True
        ) as render_page:
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf")
        self.assertEqual(caught.exception.status_code, 413)
        render_page.assert_not_called()
        fake_pytesseract.image_to_string.assert_not_called()

    def test_renderer_output_dimension_is_checked_after_rasterization(self):
        class OversizedPixmap:
            width = 20_001
            height = 1

            def tobytes(self, kind):
                raise AssertionError("oversized bitmap must not be encoded")

        fake_pymupdf = types.SimpleNamespace(open=lambda **kwargs: FakePdfDoc(1))
        fake_pytesseract = types.SimpleNamespace(image_to_string=MagicMock(return_value="must not run"))
        fake_image = types.SimpleNamespace(open=lambda value: object())
        fake_pil = types.ModuleType("PIL")
        fake_pil.Image = fake_image
        with patch.dict(sys.modules, {
            "pymupdf": fake_pymupdf,
            "pytesseract": fake_pytesseract,
            "PIL": fake_pil,
        }), patch.object(FakePdfPage, "get_pixmap", return_value=OversizedPixmap()):
            with self.assertRaises(app.HTTPException) as caught:
                app.ocr_pdf_text(b"pdf")
        self.assertEqual(caught.exception.status_code, 413)
        fake_pytesseract.image_to_string.assert_not_called()



if __name__ == "__main__":
    unittest.main()
