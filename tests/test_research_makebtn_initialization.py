"""Regression test for Legal Research helper initialization order."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")
LAW = HTML[HTML.index("async function law()"):HTML.index("\nasync function ", HTML.index("async function law()") + 30)]


class ResearchMakeButtonInitializationTests(unittest.TestCase):
    def test_make_button_helper_is_hoisted_before_early_page_setup(self):
        declaration = LAW.index("function makeBtn(label,fn,cl='g')")
        first_use = LAW.index("makeBtn(")
        self.assertLess(declaration, first_use)
        self.assertNotIn("const makeBtn=", LAW)


if __name__ == "__main__":
    unittest.main()
