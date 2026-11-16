"""Regression contract for Legal Research copy helper hoisting."""
from pathlib import Path
import re
import unittest

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")
LAW = HTML[HTML.index("async function law()"):HTML.index("\nasync function ", HTML.index("async function law()") + 30)]


class ResearchCopyInitializationTests(unittest.TestCase):
    def test_copy_helper_is_a_hoisted_function_declaration(self):
        self.assertRegex(LAW, re.compile(r"function copy\(v\)\s*\{\s*return LANG==='ar'\?v:"))
        self.assertNotIn("const copy=", LAW)


if __name__ == "__main__":
    unittest.main()
