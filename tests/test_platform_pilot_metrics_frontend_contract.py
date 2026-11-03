"""Contract checks for the platform-only pilot metrics view."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class PlatformPilotMetricsFrontendContractTests(unittest.TestCase):
    def test_metrics_view_is_linked_only_for_platform_admins(self):
        self.assertIn("platformPilotMetricsPage", HTML)
        self.assertIn("ME.platform_roles.includes('platform_admin')", HTML)
        self.assertIn("View usage metrics", HTML)
        self.assertIn("عرض مؤشرات الاستخدام", HTML)

    def test_view_discloses_aggregate_only_active_user_semantics_and_exports_csv(self):
        self.assertIn("/platform/pilot-metrics?weeks=12", HTML)
        self.assertIn("/platform/pilot-metrics.csv?weeks=12", HTML)
        self.assertIn("not distinct people", HTML)
        self.assertIn("لا تُحفظ أسئلة أو إجابات أو بيانات قضايا أو معرفات مستخدمين", HTML)
        for metric in (
            "active_users", "cases_created", "deadlines_created",
            "answers_requested", "invoices_issued", "corrections_submitted",
        ):
            self.assertIn(metric, HTML)


if __name__ == "__main__":
    unittest.main()
