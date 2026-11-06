"""Contract checks for the platform-only pilot metrics view."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "static" / "index.html").read_text(encoding="utf-8")


class PlatformPilotMetricsFrontendContractTests(unittest.TestCase):
    def test_metrics_view_is_linked_only_for_platform_admins(self):
        self.assertIn("platformPilotMetricsPage", HTML)
        self.assertIn("ME.platform_roles.includes('platform_admin')", HTML)
        self.assertIn("View pilot metrics", HTML)
        self.assertIn("مؤشرات استخدام المكاتب", HTML)

    def test_view_discloses_counts_only_sign_in_semantics_and_exports_csv(self):
        self.assertIn("/platform/pilot-metrics?weeks=12", HTML)
        self.assertIn("/platform/pilot-metrics/export.csv?weeks=12", HTML)
        self.assertIn("Successful sign-ins", HTML)
        self.assertIn("Weekly active users", HTML)
        self.assertIn("not distinct people", HTML)
        self.assertIn("case/task/calendar-only activity is not currently included", HTML.lower())
        self.assertIn("المستخدمون النشطون أسبوعياً", HTML)
        self.assertIn("معرفات المستخدمين", HTML)


if __name__ == "__main__":
    unittest.main()
