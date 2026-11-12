import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONL = ROOT / "tests" / "legal_eval" / "multi_area_questions.draft.jsonl"
CSV = ROOT / "tests" / "legal_eval" / "multi_area_questions_for_lawyer.csv"


class MultiAreaDraftBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = [json.loads(line) for line in JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
        with CSV.open(encoding="utf-8-sig", newline="") as f:
            cls.csv_rows = list(csv.DictReader(f))

    def test_benchmark_has_expected_size_and_area_coverage(self):
        self.assertEqual(len(self.questions), 100)
        self.assertEqual(len(self.csv_rows), 100)
        self.assertEqual(len({q["id"] for q in self.questions}), 100)
        counts = {}
        for q in self.questions:
            counts[q["practice_area"]] = counts.get(q["practice_area"], 0) + 1
        self.assertEqual(counts, {
            "rent_and_tenancy": 15,
            "personal_status": 15,
            "civil_procedure": 13,
            "civil_law": 13,
            "criminal_procedure": 10,
            "commercial_law": 9,
            "tax_law": 8,
            "social_insurance": 6,
            "real_estate": 6,
            "data_protection": 5,
        })

    def test_all_questions_remain_unreviewed_and_unscoreable(self):
        expected_fields = {
            "id", "practice_area", "question_type", "question_ar", "as_of_date",
            "expected_answer", "expected_sources", "expected_pin_cites", "answerable",
            "must_abstain_if_unverified", "review_status", "reviewer_name",
            "reviewer_role", "review_evidence_url", "review_date", "must_abstain",
        }
        for q in self.questions:
            with self.subTest(question=q["id"]):
                self.assertEqual(set(q), expected_fields)
                self.assertEqual(q["review_status"], "needs_lawyer_review")
                self.assertIsNone(q["answerable"])
                self.assertIsNone(q["expected_answer"])
                self.assertEqual(q["expected_sources"], [])
                self.assertEqual(q["expected_pin_cites"], [])
                self.assertTrue(q["must_abstain_if_unverified"])
                self.assertIsNone(q["reviewer_name"])
                self.assertIsNone(q["reviewer_role"])
                self.assertIsNone(q["review_evidence_url"])
                self.assertIsNone(q["review_date"])

    def test_seven_explicit_abstention_cases_and_csv_jsonl_id_parity(self):
        abstain = [q for q in self.questions if q["must_abstain"]]
        self.assertEqual(len(abstain), 7)
        self.assertTrue(all(q["must_abstain_if_unverified"] is True for q in self.questions))
        self.assertEqual({q["id"] for q in self.questions}, {r["id"] for r in self.csv_rows})
        by_id = {q["id"]: q for q in self.questions}
        for row in self.csv_rows:
            q = by_id[row["id"]]
            self.assertEqual(row["السؤال"], q["question_ar"])
            self.assertEqual(row["مجال القانون"], q["practice_area"])
            self.assertEqual(row["هل يجب الامتناع؟ (نعم/لا)"].strip() == "نعم", q["must_abstain"])
            self.assertEqual(row["الإجابة الصحيحة (يملؤها المحامي)"], "")
            self.assertEqual(row["المصدر: القانون/المادة/عدد الجريدة"], "")
            self.assertEqual(row["ملاحظات"], "")
            self.assertEqual(row["اسم المراجع"], "")
            self.assertEqual(row["تاريخ المراجعة"], "")
            self.assertEqual(row["صفة المراجع"], "")
            self.assertEqual(row["رابط دليل المراجعة"], "")


if __name__ == "__main__":
    unittest.main()
