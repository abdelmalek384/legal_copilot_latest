"""Regression checks for the self-hosted Legal Copilot design system."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "static" / "design-tokens.css").read_text(encoding="utf-8")
APP = (ROOT / "app.py").read_text(encoding="utf-8")


def contrast_ratio(foreground, background):
    def luminance(value):
        channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    first, second = luminance(foreground), luminance(background)
    return (max(first, second) + 0.05) / (min(first, second) + 0.05)


class DesignTokensContractTests(unittest.TestCase):
    def test_tokens_are_loaded_from_one_same_origin_stylesheet(self):
        self.assertIn('<link rel="stylesheet" href="/static/design-tokens.css">', HTML)
        self.assertNotIn('<style id="design-tokens">', HTML)
        self.assertEqual(CSS.count(":root{"), 1)
        self.assertIn("style-src 'self' 'unsafe-inline'", APP)
        self.assertNotRegex(CSS, r"@import\s+url|url\(\s*https?://")


    def test_arabic_font_is_self_hosted_and_open_font_licensed(self):
        font = ROOT / "static" / "fonts" / "NotoNaskhArabic-VF.ttf"
        license_file = ROOT / "static" / "fonts" / "OFL.txt"
        self.assertTrue(font.is_file())
        self.assertGreater(font.stat().st_size, 100_000)
        self.assertIn('src:url("/static/fonts/NotoNaskhArabic-VF.ttf")', CSS)
        self.assertIn('font-weight:100 900', CSS)
        self.assertIn('html[lang="ar"] body{font-family:"LegalCopilot Naskh"', CSS)
        self.assertIn("SIL OPEN FONT LICENSE Version 1.1", license_file.read_text(encoding="utf-8"))
        self.assertIn("font-src 'self' data:", APP)
        self.assertIn('@app.get("/static/fonts/NotoNaskhArabic-VF.ttf")', APP)
        self.assertIn('@app.get("/static/fonts/OFL.txt")', APP)
        self.assertIn('@app.get("/static/design-tokens.css")', APP)
        self.assertIn('media_type="font/ttf"', APP)
        self.assertIn('media_type="text/css"', APP)
        self.assertNotIn('app.mount("/static"', APP)

    def test_palette_has_accessible_navy_gold_and_muted_text(self):
        ivory = "#f8f6f0"
        for foreground in ("#14284b", "#775b25", "#596575"):
            self.assertGreaterEqual(contrast_ratio(foreground, ivory), 4.5)

    def test_typography_spacing_shadows_and_touch_targets_are_tokenized(self):
        for token in (
            "--space-1:8px", "--space-2:16px", "--space-3:24px",
            "--space-4:32px", "--font-body:16px", "--font-arabic:17px",
            "--font-caption:13px", '--font-title:"LegalCopilot Naskh",Georgia', "--shadow-soft:",
            "--shadow-raised:", "--tap-target:44px",
        ):
            self.assertIn(token, CSS)
        self.assertIn('font-family:var(--font-title)', CSS)
        self.assertIn("button,.tabs a,#side a{min-height:var(--tap-target)}", CSS)

if __name__ == "__main__":
    unittest.main()
