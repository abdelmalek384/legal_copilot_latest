import os
import unittest
from unittest.mock import MagicMock, patch

from identity_email import IdentityEmailError, send_identity_email


class IdentityEmailAdapterTests(unittest.TestCase):
    def setUp(self):
        self.env_names = (
            "COPILOT_EMAIL_SMTP_HOST", "COPILOT_EMAIL_SMTP_PORT",
            "COPILOT_EMAIL_SMTP_USERNAME", "COPILOT_EMAIL_SMTP_PASSWORD",
            "COPILOT_EMAIL_SMTP_SECURITY", "COPILOT_EMAIL_FROM", "COPILOT_ENV",
        )
        self.old_env = {name: os.environ.get(name) for name in self.env_names}
        for name in self.env_names:
            os.environ.pop(name, None)

    def tearDown(self):
        for name, value in self.old_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_missing_delivery_configuration_fails_closed(self):
        with self.assertRaisesRegex(IdentityEmailError, "must be configured"):
            send_identity_email("person@example.test", "Test", "body")

    def test_starttls_delivery_uses_tls_and_never_logs_message(self):
        os.environ.update({
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_SMTP_PORT": "587",
            "COPILOT_EMAIL_SMTP_USERNAME": "smtp-user",
            "COPILOT_EMAIL_SMTP_PASSWORD": "smtp-secret",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_ENV": "production",
        })
        server = MagicMock()
        server.__enter__.return_value = server
        with patch("identity_email.smtplib.SMTP", return_value=server) as smtp:
            send_identity_email("recipient@example.test", "One-time link", "private-token-body")
        smtp.assert_called_once_with("smtp.example.test", 587, timeout=10)
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("smtp-user", "smtp-secret")
        sent = server.send_message.call_args.args[0]
        self.assertEqual(sent["To"], "recipient@example.test")
        self.assertIn("private-token-body", sent.get_content())
        self.assertNotIn("smtp-secret", repr(sent))

    def test_plain_smtp_is_rejected_in_production(self):
        os.environ.update({
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_SECURITY": "plain",
            "COPILOT_ENV": "production",
        })
        with patch("identity_email.smtplib.SMTP") as smtp:
            with self.assertRaisesRegex(IdentityEmailError, "disabled in production"):
                send_identity_email("recipient@example.test", "Subject", "body")
        smtp.assert_not_called()

    def test_header_injection_is_rejected_before_sending(self):
        os.environ.update({
            "COPILOT_EMAIL_SMTP_HOST": "smtp.example.test",
            "COPILOT_EMAIL_FROM": "noreply@example.test",
            "COPILOT_EMAIL_SMTP_SECURITY": "starttls",
        })
        with patch("identity_email.smtplib.SMTP") as smtp:
            with self.assertRaises(IdentityEmailError):
                send_identity_email("person@example.test\r\nBcc: victim@example.test", "Subject", "body")
        smtp.assert_not_called()


if __name__ == "__main__":
    unittest.main()
