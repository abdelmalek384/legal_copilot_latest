"""Regression test for Legal Research helper initialization semantics."""
from pathlib import Path
import re
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")
LAW = HTML[HTML.index("async function law()"):HTML.index("\nasync function ", HTML.index("async function law()") + 30)]


class ResearchMakeButtonInitializationTests(unittest.TestCase):
    def test_make_button_helper_uses_hoisted_function_declaration(self):
        self.assertRegex(LAW, re.compile(r"function makeBtn\(label,fn,cl='g'\)\s*\{\s*return btn\(copy\(label\),fn,cl\)\s*\}"))
        self.assertNotIn("const makeBtn=", LAW)


if __name__ == "__main__":
    unittest.main()
