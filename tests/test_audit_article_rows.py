import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.audit_article_rows import audit, load_rows, main, quantity_checklist  # noqa: E402

# Synthetic text for tests only; it is not real law.
BASE = "نص تجريبي للمادة رقم {n} من القانون التجريبي ويستمر العمل به فى الحالات المبينة."


def make_rows(count=25, law="قانون تجريبي"):
    return [{"law": law, "article": str(n), "text": BASE.format(n=n), "verified": "0", "in_force": "1", "as_of": "2025-05-03"}
            for n in range(1, count + 1)]


class AuditArticleRowsTests(unittest.TestCase):
    def test_clean_rows_have_no_findings(self):
        report = audit(make_rows())
        info = report["numbering"]["قانون تجريبي"]
        self.assertEqual((info["first"], info["last"], info["gaps"], info["duplicates"]), (1, 25, [], []))
        self.assertTrue(info["in_order"])
        self.assertEqual(report["findings"], {})
        self.assertEqual(report["exact_duplicate_texts"], [])

    def test_gap_duplicate_and_order_detected(self):
        rows = make_rows()
        del rows[4]
        rows.append(dict(rows[0]))
        info = audit(rows)["numbering"]["قانون تجريبي"]
        self.assertEqual(info["gaps"], [5])
        self.assertEqual(info["duplicates"], ["1"])
        self.assertFalse(info["in_order"])

    def test_text_quality_findings(self):
        rows = make_rows()
        rows[0]["text"] = ""
        rows[1]["text"] = "قصير"
        rows[2]["text"] = "نص فيه حرف مخفي\u200b وبعض Latin words هنا ."
        rows[3]["text"] = "رقم ١٢ و 12 معا في النص ."
        rows[4]["text"] = "نص بلا علامة ترقيم في نهايته"
        findings = audit(rows)["findings"]
        for key in ("empty_text", "very_short_text", "hidden_or_replacement_characters", "latin_fragments",
                    "mixed_digit_systems", "no_terminal_punctuation"):
            self.assertIn(key, findings, key)

    def test_exact_duplicate_texts(self):
        rows = make_rows()
        rows[9]["text"] = rows[2]["text"]
        self.assertEqual(len(audit(rows)["exact_duplicate_texts"]), 1)

    def test_cross_reference_beyond_highest_article(self):
        rows = make_rows()
        rows[0]["text"] = "تسري أحكام المادة (99) على هذه الحالة ، والمادة (3) أيضا ."
        refs = audit(rows)["cross_references"]
        self.assertEqual([r["ref"] for r in refs["beyond_highest_article_in_file"]], ["99"])

    def test_orthography_outliers_are_listed(self):
        rows = make_rows(40)
        rows[7]["text"] = "ويحظر في جميع الأحوال ذلك ."
        outliers = audit(rows)["orthography"]["minority_style_rows"]
        self.assertEqual(len(outliers), 1)
        self.assertTrue(outliers[0]["row"].endswith("/ 8"))

    def test_quantity_checklist_finds_periods_amounts_and_skips_references_and_list_markers(self):
        rows = make_rows(3)
        rows[0]["text"] = "للعامل إجازة مدتها ثلاثين يوما ومكافأة 500 جنيه ونسبة 5% من الأجر ."
        rows[1]["text"] = "1- العامل : كل شخص . 2- صاحب العمل : كل شخص . وفقا للقانون رقم 12 لسنة 2003 والمادة (5) ."
        items = quantity_checklist(rows)
        self.assertEqual([i["article"] for i in items], ["1"])
        joined = " ".join(items[0]["snippets"])
        self.assertIn("ثلاثين يوما", joined)
        self.assertIn("500 جنيه", joined)

    def test_embedded_flags_are_reported_not_trusted(self):
        flags = audit(make_rows())["embedded_flags"]
        self.assertEqual(flags["verified"], {"0": 25})
        self.assertEqual(flags["in_force"], {"1": 25})

    def test_cli_writes_outputs_and_handles_bad_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "rows.jsonl"
            src.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in make_rows()) + "\nnot json\n", encoding="utf-8")
            out = Path(tmp) / "out"
            self.assertEqual(main(["--input", str(src), "--out-dir", str(out)]), 0)
            for name in ("audit.json", "audit.md", "quantity_checklist.csv"):
                self.assertTrue((out / name).exists(), name)
            self.assertEqual(json.loads((out / "audit.json").read_text(encoding="utf-8"))["malformed_lines"], 1)
            empty = Path(tmp) / "empty.jsonl"
            empty.write_text("", encoding="utf-8")
            self.assertEqual(main(["--input", str(empty), "--out-dir", str(out)]), 2)


if __name__ == "__main__":
    unittest.main()
