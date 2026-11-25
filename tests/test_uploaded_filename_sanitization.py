"""Upload filename normalization rejects Unicode controls and bidi format markers."""
import unittest
import app

class UploadedFilenameSanitizationTests(unittest.TestCase):
    def test_removes_path_components(self):
        self.assertEqual(app._sanitize_uploaded_filename(r"C:\secret\matter.pdf"), "matter.pdf")

    def test_removes_bidi_format_controls(self):
        hostile = "report\u202eexe.pdf\u2066"
        self.assertEqual(app._sanitize_uploaded_filename(hostile), "reportexe.pdf")

    def test_removes_other_unicode_format_and_control_characters(self):
        hostile = "matter\u200b\x01\x7f.pdf"
        self.assertEqual(app._sanitize_uploaded_filename(hostile), "matter.pdf")

    def test_trims_and_caps_length(self):
        self.assertEqual(app._sanitize_uploaded_filename("  " + "x" * 250), "x" * 200)

    def test_empty_or_filtered_name_falls_back(self):
        self.assertEqual(app._sanitize_uploaded_filename("\u202e\u200b"), "doc")

if __name__ == "__main__":
    unittest.main()
