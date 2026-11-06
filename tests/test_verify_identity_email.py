import json
import os
import unittest
from unittest.mock import patch

from tools import verify_identity_email


class VerifyIdentityEmailTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "COPILOT_ENV": "staging",
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
        }, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_requires_controlled_mailbox_confirmation_before_sending(self):
        with patch.object(verify_identity_email, "send_identity_email") as send:
            with self.assertRaises(SystemExit):
                verify_identity_email.main(["--recipient", "controlled@example.test"])
        send.assert_not_called()

    def test_staging_probe_reports_smtp_acceptance_not_mailbox_delivery(self):
        with patch.object(verify_identity_email, "send_identity_email") as send, patch.object(
            verify_identity_email.uuid, "uuid4"
        ) as uuid4:
            uuid4.return_value.hex = "a" * 32
            result = verify_identity_email.main([
                "--recipient", "controlled@example.test", "--confirm-controlled-mailbox"
            ])
        self.assertEqual(result, 0)
        send.assert_called_once()
        args = send.call_args.args
        self.assertEqual(args[0], "controlled@example.test")
        self.assertIn("aaaaaaaaaaaa", args[1])
        self.assertIn("Probe ID:", args[2])

    def test_production_probe_requires_separate_explicit_confirmation(self):
        os.environ["COPILOT_ENV"] = "production"
        with patch.object(verify_identity_email, "send_identity_email") as send:
            with self.assertRaises(SystemExit):
                verify_identity_email.main([
                    "--recipient", "controlled@example.test", "--confirm-controlled-mailbox"
                ])
        send.assert_not_called()

    def test_production_probe_sends_only_after_both_confirmations(self):
        os.environ["COPILOT_ENV"] = "production"
        os.environ["COPILOT_EMAIL_SMTP_SECURITY"] = "ssl"
        with patch.object(verify_identity_email, "send_identity_email") as send:
            result = verify_identity_email.main([
                "--recipient", "controlled@example.test",
                "--confirm-controlled-mailbox", "--confirm-production-send",
            ])
        self.assertEqual(result, 0)
        send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
