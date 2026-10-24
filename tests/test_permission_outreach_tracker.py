"""Guardrails for permission-outreach tracking: contact verification is not authorization."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRACKER = json.loads((ROOT / "docs" / "phase_2_permission_outreach_tracker.json").read_text(encoding="utf-8"))

class PermissionOutreachTrackerTests(unittest.TestCase):
    def test_verified_amiri_press_contact_has_official_evidence_but_is_not_sent(self):
        request = next(item for item in TRACKER["requests"] if item["request_id"] == "PERM-001")
        self.assertTrue(request["contact_verified"])
        self.assertEqual(request["contact_verified_on"], "2026-10-24")
        self.assertIn("https://www.alamiria.com/Sec/Contact-Us", request["contact_verification_evidence"])
        self.assertEqual(request["candidate_contact"], "info@alamiria.com")
        self.assertEqual(request["status"], "draft_not_sent")
        self.assertIsNone(request["sent_at"])
        self.assertEqual(request["authorized_scopes"], [])
        self.assertEqual(request["decision"], "no_permission_granted")

    def test_court_of_cassation_contact_is_verified_but_request_remains_blocked(self):
        request = next(item for item in TRACKER["requests"] if item["request_id"] == "PERM-002")
        self.assertTrue(request["contact_verified"])
        self.assertEqual(request["contact_verified_on"], "2026-10-24")
        self.assertIn("https://cc.gov.eg/", request["contact_verification_evidence"])
        self.assertEqual(request["candidate_contact"], "cc_info@cc.gov.eg")
        self.assertEqual(request["status"], "draft_not_sent")
        self.assertEqual(request["decision"], "blocked_pending_written_authorization")
        self.assertEqual(request["authorized_scopes"], [])
        self.assertIsNone(request["sent_at"])

    def test_contact_verification_does_not_grant_collection_permission(self):
        for request in TRACKER["requests"]:
            self.assertTrue(request["contact_verified"])
            self.assertIn("https://", request["contact_verification_evidence"])
            self.assertEqual(request["authorized_scopes"], [])
            self.assertIsNone(request["sent_at"])
            self.assertIn(request["decision"], {"no_permission_granted", "blocked_pending_written_authorization"})

if __name__ == "__main__":
    unittest.main()
