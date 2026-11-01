import smtplib
import unittest
from email.message import EmailMessage
from unittest.mock import patch
from tools.reminder_email import ReminderEmailError, SMTPConfig, send_reminder_email


class ReminderEmailTests(unittest.TestCase):
    def setUp(self):
        self.config = SMTPConfig("smtp.example.test", 587, "notices@example.test", "smtp-user", "not-a-real-password")
        self.reminder = {"event_type": "deadline", "due_date": "2026-10-27", "window": "due_soon", "event_id": "private-case-id"}
        self.sleep_calls = []

    def sleeper(self, seconds):
        self.sleep_calls.append(seconds)

    def test_disabled_is_default_and_does_not_call_sender(self):
        calls = []
        result = send_reminder_email(self.reminder, "user@example.test", "https://legal.example.test",
                                     self.config, send_once=lambda *args: calls.append(args))
        self.assertEqual(result["status"], "disabled")
        self.assertEqual(calls, [])

    def test_generic_content_omits_private_identifiers(self):
        captured = []
        result = send_reminder_email(self.reminder, "user@example.test", "https://legal.example.test/path",
                                     self.config, enabled=True, send_once=lambda config, message: captured.append(message))
        self.assertEqual(result["status"], "accepted_by_smtp")
        message = captured[0]
        self.assertIsInstance(message, EmailMessage)
        body = message.get_content()
        self.assertIn("case deadline", body)
        self.assertIn("2026-10-27", body)
        self.assertIn("https://legal.example.test/path/", body)
        self.assertNotIn("private-case-id", body)
        self.assertNotIn("client names", message["Subject"].lower())

    def test_retries_transient_errors_with_exponential_backoff(self):
        calls = []
        def sender(config, message):
            calls.append(1)
            if len(calls) < 3:
                raise smtplib.SMTPResponseException(451, b"secret provider response")
        result = send_reminder_email(self.reminder, "user@example.test", "https://legal.example.test",
                                     self.config, enabled=True, max_attempts=3, base_backoff_seconds=2,
                                     send_once=sender, sleep=self.sleeper)
        self.assertEqual(result["status"], "accepted_by_smtp")
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(self.sleep_calls, [2.0, 4.0])

    def test_timeout_after_send_message_starts_is_ambiguous_and_never_retried(self):
        class FakeSMTP:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def ehlo(self):
                pass
            def starttls(self, context=None):
                pass
            def login(self, username, password):
                pass
            def send_message(self, message):
                raise TimeoutError("provider accepted then lost the response")

        with patch("tools.reminder_email.smtplib.SMTP", return_value=FakeSMTP()):
            result = send_reminder_email(
                self.reminder, "user@example.test", "https://legal.example.test", self.config,
                enabled=True, max_attempts=5, base_backoff_seconds=0, sleep=self.sleeper,
            )

        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["error_code"], "smtp_submission_ambiguous")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(self.sleep_calls, [])
        self.assertNotIn("provider accepted", str(result))

    def test_pre_submission_connection_failure_can_be_retried(self):
        class FakeSMTP:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def ehlo(self):
                pass
            def starttls(self, context=None):
                pass
            def login(self, username, password):
                pass
            def send_message(self, message):
                return {}

        factories = []
        def smtp_factory(*args, **kwargs):
            factories.append(1)
            if len(factories) == 1:
                raise TimeoutError("connect failed before DATA")
            return FakeSMTP()

        with patch("tools.reminder_email.smtplib.SMTP", side_effect=smtp_factory):
            result = send_reminder_email(
                self.reminder, "user@example.test", "https://legal.example.test", self.config,
                enabled=True, max_attempts=3, base_backoff_seconds=2, sleep=self.sleeper,
            )

        self.assertEqual(result["status"], "accepted_by_smtp")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(factories), 2)
        self.assertEqual(self.sleep_calls, [2.0])

    def test_close_error_after_confirmed_smtp_acceptance_does_not_resend(self):
        class FakeSMTP:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                raise OSError("QUIT failed after server accepted DATA")
            def ehlo(self):
                pass
            def starttls(self, context=None):
                pass
            def login(self, username, password):
                pass
            def send_message(self, message):
                return {}

        with patch("tools.reminder_email.smtplib.SMTP", return_value=FakeSMTP()):
            result = send_reminder_email(
                self.reminder, "user@example.test", "https://legal.example.test", self.config,
                enabled=True, max_attempts=5, base_backoff_seconds=0, sleep=self.sleeper,
            )

        self.assertEqual(result["status"], "accepted_by_smtp")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(self.sleep_calls, [])

    def test_explicit_smtp_4xx_rejection_is_retryable(self):
        calls = []
        class FakeSMTP:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def ehlo(self):
                pass
            def starttls(self, context=None):
                pass
            def login(self, username, password):
                pass
            def send_message(self, message):
                calls.append(1)
                if len(calls) == 1:
                    raise smtplib.SMTPDataError(451, b"temporary rejection")
                return {}

        with patch("tools.reminder_email.smtplib.SMTP", side_effect=lambda *args, **kwargs: FakeSMTP()):
            result = send_reminder_email(
                self.reminder, "user@example.test", "https://legal.example.test", self.config,
                enabled=True, max_attempts=3, base_backoff_seconds=1, sleep=self.sleeper,
            )

        self.assertEqual(result["status"], "accepted_by_smtp")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(calls), 2)
        self.assertEqual(self.sleep_calls, [1.0])

    def test_auth_failure_is_not_retried_and_error_is_sanitized(self):
        calls = []
        def sender(config, message):
            calls.append(1)
            raise smtplib.SMTPAuthenticationError(535, b"secret password detail")
        result = send_reminder_email(self.reminder, "user@example.test", "https://legal.example.test",
                                     self.config, enabled=True, send_once=sender, sleep=self.sleeper)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_code"], "smtp_authentication_failed")
        self.assertEqual(result["attempts"], 1)
        self.assertNotIn("secret", str(result))
        self.assertEqual(self.sleep_calls, [])

    def test_transient_exhaustion_is_reported(self):
        def sender(config, message):
            raise TimeoutError("provider secrets and details")
        result = send_reminder_email(self.reminder, "user@example.test", "https://legal.example.test",
                                     self.config, enabled=True, max_attempts=2, base_backoff_seconds=0,
                                     send_once=sender, sleep=self.sleeper)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(result["error_code"], "smtp_connection_failure")
        self.assertNotIn("provider secrets", str(result))

    def test_invalid_recipient_header_injection_and_url_are_rejected(self):
        for recipient in ("", "not-an-email", "a@example.test\r\nBcc: x@example.test"):
            with self.subTest(recipient=recipient), self.assertRaises(ReminderEmailError):
                send_reminder_email(self.reminder, recipient, "https://legal.example.test",
                                    self.config, enabled=True, send_once=lambda *args: None)
        for url in ("http://legal.example.test", "https://user:pass@legal.example.test",
                    "https://legal.example.test/?token=secret", "https://legal.example.test/#fragment"):
            with self.subTest(url=url), self.assertRaises(ReminderEmailError):
                send_reminder_email(self.reminder, "user@example.test", url,
                                    self.config, enabled=True, send_once=lambda *args: None)


    def test_unhashable_payload_values_fail_with_domain_error(self):
        for reminder in (dict(self.reminder, event_type=[]), dict(self.reminder, window={})):
            with self.subTest(reminder=reminder), self.assertRaises(ReminderEmailError):
                send_reminder_email(reminder, "user@example.test", "https://legal.example.test",
                                    self.config, enabled=True, send_once=lambda *args: None)
        with self.assertRaises(ReminderEmailError):
            send_reminder_email(self.reminder, "user@example.test", "https://[invalid",
                                self.config, enabled=True, send_once=lambda *args: None)
        with self.assertRaises(ReminderEmailError):
            SMTPConfig([], 587, "notices@example.test", "user", "password").validated()
        with self.assertRaises(ReminderEmailError):
            SMTPConfig("smtp.example.test", 587, "notices@example.test", "user", "password",
                       security=[]).validated()


    def test_permanent_smtp_failure_is_not_retried_and_attempts_are_bounded(self):
        calls = []
        def sender(config, message):
            calls.append(1)
            raise smtplib.SMTPResponseException(550, b"private provider response")
        result = send_reminder_email(
            self.reminder, "user@example.test", "https://legal.example.test", self.config,
            enabled=True, max_attempts=5, send_once=sender, sleep=self.sleeper,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error_code"], "smtp_permanent_failure")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(len(calls), 1)
        self.assertNotIn("private provider response", str(result))
        for attempts in (0, 6, True):
            with self.subTest(attempts=attempts), self.assertRaises(ReminderEmailError):
                send_reminder_email(
                    self.reminder, "user@example.test", "https://legal.example.test", self.config,
                    enabled=True, max_attempts=attempts, send_once=lambda *args: None,
                )

    def test_invalid_date_and_unsupported_window_rejected(self):
        for reminder in (dict(self.reminder, due_date="2026-02-30"),
                         dict(self.reminder, window="immediate"),
                         dict(self.reminder, event_type="client_name")):
            with self.subTest(reminder=reminder), self.assertRaises(ReminderEmailError):
                send_reminder_email(reminder, "user@example.test", "https://legal.example.test",
                                    self.config, enabled=True, send_once=lambda *args: None)

    def test_configuration_environment_validation(self):
        with self.assertRaises(ReminderEmailError):
            SMTPConfig.from_env({})
        config = SMTPConfig.from_env({
            "REMINDER_SMTP_HOST": "smtp.example.test", "REMINDER_SMTP_PORT": "587",
            "REMINDER_SMTP_SENDER": "notices@example.test", "REMINDER_SMTP_USERNAME": "smtp-user",
            "REMINDER_SMTP_PASSWORD": "secret", "REMINDER_SMTP_SECURITY": "starttls",
        })
        self.assertEqual(config.port, 587)
        with self.assertRaises(ReminderEmailError):
            SMTPConfig("smtp.example.test", 25, "bad", "u", "p").validated()


if __name__ == "__main__":
    unittest.main()
