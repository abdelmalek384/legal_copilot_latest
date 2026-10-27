import datetime as dt
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import deadline_calculator as dc

D = dt.date


class DeadlineCalculatorTests(unittest.TestCase):
    def calc(self, trigger, amount, unit, **kw):
        kw.setdefault("allow_unverified", True)
        return dc.compute_deadline(trigger, amount, unit, **kw)

    def test_day_count_and_weekend_extension(self):
        r = self.calc(D(2026, 10, 26), 40, "days")
        self.assertEqual(r["raw_end"], "2026-12-05")
        self.assertEqual(r["final_due"], "2026-12-06")
        self.assertEqual(r["extensions"][0]["reason"], "عطلة أسبوعية")

    def test_month_end_and_leap_year_arithmetic(self):
        self.assertEqual(self.calc(D(2026, 1, 31), 1, "months")["raw_end"], "2026-02-28")
        self.assertEqual(self.calc(D(2024, 2, 29), 1, "years")["raw_end"], "2025-02-28")

    def test_distance_days_are_added_before_extension(self):
        r = self.calc(D(2026, 10, 26), 3, "days", distance_days=2)
        self.assertEqual(r["raw_end"], "2026-10-29")
        self.assertEqual(r["final_due"], "2026-11-01")

    def test_official_holiday_candidate_extends_but_is_unverified_data(self):
        holidays, complete = dc.load_holidays(years=[2026])
        r = self.calc(D(2026, 10, 1), 5, "days", holidays=holidays, complete_holiday_years=complete)
        self.assertEqual(r["raw_end"], "2026-10-06")
        self.assertEqual(r["final_due"], "2026-10-07")
        self.assertTrue(r["warnings"])

    def test_direct_arithmetic_cannot_claim_a_rule_was_verified(self):
        with self.assertRaises(TypeError):
            dc.compute_deadline(
                D(2026, 10, 26), 60, "days",
                verified_rule=True, allow_unverified=False,
            )

    def test_unverified_rule_refused_by_default(self):
        rule = dc.load_rules()["civil_cassation_60d"]
        with self.assertRaises(dc.UnverifiedRuleError):
            dc.compute_from_rule(rule, D(2026, 10, 26))

    def test_verified_requires_source_reviewer_and_valid_date(self):
        rule = dict(dc.load_rules()["civil_cassation_60d"], verified=True,
                    verified_by="Reviewer", verified_on="2026-10-26", source_article="Article X")
        self.assertTrue(dc.compute_from_rule(rule, D(2026, 10, 26))["verified_rule"])
        for key, value in (("verified_by", " "), ("verified_on", "tomorrow"), ("source_article", "")):
            bad = dict(rule, **{key: value})
            with self.assertRaises(dc.UnverifiedRuleError):
                dc.compute_from_rule(bad, D(2026, 10, 26))

    def test_datetime_and_bad_weekdays_rejected(self):
        with self.assertRaises(dc.DeadlineError):
            self.calc(dt.datetime(2026, 10, 26, 12, 0), 3, "days")
        for weekdays in ((7,), (-1,), (True,), (4, 4)):
            with self.assertRaises(dc.DeadlineError):
                self.calc(D(2026, 10, 26), 3, "days", non_working_weekdays=weekdays)

    def test_bad_distance_bool_and_malformed_json_fail_cleanly(self):
        with self.assertRaises(dc.DeadlineError):
            self.calc(D(2026, 10, 26), 3, "days", distance_days=True)
        with self.assertRaises(dc.DeadlineError):
            dc.load_rules(Path("missing-rules-file.json"))

    def test_cli_refuses_unverified_draft_and_warns_when_overridden(self):
        import contextlib, io
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(dc.main(["--rule", "civil_cassation_60d", "--from", "2026-10-26"]), 2)
        self.assertIn("refusing", err.getvalue())
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(dc.main(["--rule", "civil_cassation_60d", "--from", "2026-10-26", "--allow-unverified", "--json"]), 0)
        result = json.loads(out.getvalue())
        self.assertFalse(result["verified_rule"])
        self.assertTrue(result["warnings"])
        self.assertIn("disclaimer", result)

    def test_manual_inputs_are_bounded(self):
        for value in (0, -1, 3651, True, 2.5, "3"):
            with self.assertRaises(dc.DeadlineError):
                self.calc(D(2026, 10, 26), value, "days")
        with self.assertRaises(dc.DeadlineError):
            self.calc(D(2026, 10, 26), 3, "weeks")


if __name__ == "__main__":
    unittest.main()
