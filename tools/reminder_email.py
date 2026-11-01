#!/usr/bin/env python3
"""Privacy-safe SMTP adapter for reminder plans.

Independent of the application's database. Sends only generic reminders from a
pre-authorized caller and reports SMTP acceptance, not inbox delivery.
"""
from __future__ import annotations
import os, re, smtplib, ssl, time
from dataclasses import dataclass
from datetime import date
from email.message import EmailMessage
from typing import Callable, Mapping
from urllib.parse import urlsplit


class ReminderEmailError(ValueError):
    """Raised when configuration or a reminder payload is unsafe."""


class SMTPSubmissionAmbiguous(Exception):
    """SMTP transport failed after message submission began; do not retry automatically."""


@dataclass(frozen=True)
class SMTPConfig:
    host: str
    port: int
    sender: str
    username: str
    password: str
    security: str = "starttls"
    timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "SMTPConfig":
        env = os.environ if environ is None else environ
        required = ("REMINDER_SMTP_HOST", "REMINDER_SMTP_SENDER",
                    "REMINDER_SMTP_USERNAME", "REMINDER_SMTP_PASSWORD")
        missing = [name for name in required if not str(env.get(name, "")).strip()]
        if missing:
            raise ReminderEmailError("Missing required SMTP settings: " + ", ".join(missing))
        try:
            port = int(env.get("REMINDER_SMTP_PORT", "587"))
            timeout = float(env.get("REMINDER_SMTP_TIMEOUT", "10"))
        except (TypeError, ValueError) as exc:
            raise ReminderEmailError("SMTP port and timeout must be numeric") from exc
        return cls(str(env["REMINDER_SMTP_HOST"]).strip(), port,
                   str(env["REMINDER_SMTP_SENDER"]).strip(),
                   str(env["REMINDER_SMTP_USERNAME"]).strip(),
                   str(env["REMINDER_SMTP_PASSWORD"]),
                   str(env.get("REMINDER_SMTP_SECURITY", "starttls")).strip().lower(),
                   timeout).validated()

    def validated(self) -> "SMTPConfig":
        if not isinstance(self.host, str) or not self.host.strip() or any(ch in self.host for ch in "\r\n"):
            raise ReminderEmailError("SMTP host is invalid")
        if type(self.port) is not int or not 1 <= self.port <= 65535:
            raise ReminderEmailError("SMTP port must be between 1 and 65535")
        if not isinstance(self.security, str) or self.security not in {"starttls", "ssl"}:
            raise ReminderEmailError("SMTP security must be starttls or ssl")
        if isinstance(self.timeout_seconds, bool) or not isinstance(self.timeout_seconds, (int, float)) or not 1 <= self.timeout_seconds <= 60:
            raise ReminderEmailError("SMTP timeout must be between 1 and 60 seconds")
        _validate_email(self.sender, "sender")
        if not isinstance(self.username, str) or not self.username.strip() or not isinstance(self.password, str) or not self.password:
            raise ReminderEmailError("SMTP username and password must be configured")
        return self


def _validate_email(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 254:
        raise ReminderEmailError(f"{label} must be a valid email address")
    value = value.strip()
    if any(ch in value for ch in "\r\n") or not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", value):
        raise ReminderEmailError(f"{label} must be a valid email address")
    return value


def _safe_message(reminder: Mapping[str, object], recipient: str, app_url: str, sender: str) -> EmailMessage:
    if not isinstance(reminder, Mapping):
        raise ReminderEmailError("reminder must be an object")
    kind, due_date, window = reminder.get("event_type"), reminder.get("due_date"), reminder.get("window")
    if not isinstance(kind, str) or kind not in {"task", "deadline", "session"}:
        raise ReminderEmailError("reminder event_type is unsupported")
    if not isinstance(due_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_date):
        raise ReminderEmailError("reminder due_date must use YYYY-MM-DD form")
    try:
        if date.fromisoformat(due_date).isoformat() != due_date:
            raise ValueError
    except ValueError as exc:
        raise ReminderEmailError("reminder due_date must be a real calendar date") from exc
    if not isinstance(window, str) or window not in {"due_soon", "due_today", "overdue"}:
        raise ReminderEmailError("reminder window is unsupported")
    if not isinstance(app_url, str):
        raise ReminderEmailError("application URL must be HTTPS")
    try:
        parsed = urlsplit(app_url)
    except ValueError as exc:
        raise ReminderEmailError("application URL must be a valid HTTPS base URL") from exc
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ReminderEmailError("application URL must be a clean HTTPS base URL without credentials, query, or fragment")
    recipient = _validate_email(recipient, "recipient")
    message = EmailMessage()
    message["To"] = recipient
    message["From"] = _validate_email(sender, "sender")
    message["Subject"] = "Legal Copilot reminder"
    window_text = {"due_soon": "is due soon", "due_today": "is due today", "overdue": "is overdue"}[str(window)]
    kind_text = {"task": "A task", "deadline": "A case deadline", "session": "A session"}[str(kind)]
    message.set_content(
        f"{kind_text} {window_text} (date: {due_date}).\n\n"
        f"Sign in to Legal Copilot to review it: {app_url.rstrip('/')}/\n\n"
        "This email intentionally omits client names and matter details. "
        "The date is a reminder of a recorded item, not legal advice or a legal-deadline calculation."
    )
    return message


def _smtp_send(config: SMTPConfig, message: EmailMessage) -> None:
    config.validated()
    context = ssl.create_default_context()
    submission_started = False
    submission_confirmed = False
    try:
        if config.security == "ssl":
            with smtplib.SMTP_SSL(config.host, config.port, timeout=config.timeout_seconds, context=context) as client:
                client.login(config.username, config.password)
                submission_started = True
                refused = client.send_message(message)
                if refused:
                    raise smtplib.SMTPRecipientsRefused(refused)
                submission_confirmed = True
        else:
            with smtplib.SMTP(config.host, config.port, timeout=config.timeout_seconds) as client:
                client.ehlo()
                client.starttls(context=context)
                client.ehlo()
                client.login(config.username, config.password)
                submission_started = True
                refused = client.send_message(message)
                if refused:
                    raise smtplib.SMTPRecipientsRefused(refused)
                submission_confirmed = True
    except Exception as exc:
        # A successful send_message response confirms SMTP acceptance. A later
        # QUIT/close error must not trigger a duplicate submission.
        if submission_confirmed:
            return
        # Once send_message starts, a transport failure may mean the server
        # accepted DATA but its response was lost. Quarantine rather than retry.
        is_transport_disconnect = isinstance(exc, smtplib.SMTPServerDisconnected)
        is_non_protocol_transport_error = (
            isinstance(exc, (TimeoutError, OSError)) and not isinstance(exc, smtplib.SMTPException)
        )
        if submission_started and (is_transport_disconnect or is_non_protocol_transport_error):
            raise SMTPSubmissionAmbiguous("SMTP submission outcome is ambiguous") from exc
        raise


def _is_transient(exc: Exception) -> bool:
    if isinstance(exc, smtplib.SMTPAuthenticationError):
        return False
    if isinstance(exc, smtplib.SMTPResponseException):
        return 400 <= int(getattr(exc, "smtp_code", 0)) < 500
    return isinstance(exc, (TimeoutError, OSError, smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError))


def send_reminder_email(reminder: Mapping[str, object], recipient: str, app_url: str,
                        config: SMTPConfig, *, enabled: bool = False, max_attempts: int = 3,
                        base_backoff_seconds: float = 1.0,
                        send_once: Callable[[SMTPConfig, EmailMessage], None] | None = None,
                        sleep: Callable[[float], None] = time.sleep) -> dict:
    """Send a generic reminder. Disabled by default; durable dedupe is not provided.

    accepted_by_smtp means server submission accepted, not inbox delivery. A
    timeout after submission is ambiguous; production callers need durable
    idempotency and reconciliation.
    """
    if enabled is not True:
        return {"status": "disabled", "attempts": 0, "accepted_by_smtp": False,
                "error_code": None, "warning": "Delivery is disabled; no email was sent."}
    if type(max_attempts) is not int or not 1 <= max_attempts <= 5:
        raise ReminderEmailError("max_attempts must be an integer from 1 through 5")
    if isinstance(base_backoff_seconds, bool) or not isinstance(base_backoff_seconds, (int, float)) or not 0 <= base_backoff_seconds <= 30:
        raise ReminderEmailError("base_backoff_seconds must be between 0 and 30")
    message = _safe_message(reminder, recipient, app_url, config.sender)
    sender = send_once or _smtp_send
    for attempt in range(1, max_attempts + 1):
        try:
            sender(config.validated(), message)
            return {"status": "accepted_by_smtp", "attempts": attempt,
                    "accepted_by_smtp": True, "error_code": None,
                    "warning": "SMTP acceptance is not confirmation of inbox delivery."}
        except Exception as exc:
            if isinstance(exc, SMTPSubmissionAmbiguous):
                return {
                    "status": "ambiguous", "attempts": attempt, "accepted_by_smtp": False,
                    "error_code": "smtp_submission_ambiguous",
                    "warning": "Submission may have been accepted; operator reconciliation is required and automatic retry is disabled.",
                }
            transient = _is_transient(exc)
            if transient and attempt < max_attempts:
                sleep(min(float(base_backoff_seconds) * (2 ** (attempt - 1)), 60.0))
                continue
            if isinstance(exc, smtplib.SMTPAuthenticationError):
                code = "smtp_authentication_failed"
            elif isinstance(exc, smtplib.SMTPResponseException):
                code = "smtp_transient_failure" if transient else "smtp_permanent_failure"
            elif isinstance(exc, (TimeoutError, smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, OSError)):
                code = "smtp_connection_failure"
            else:
                code = "smtp_delivery_failure"
            return {"status": "failed", "attempts": attempt, "accepted_by_smtp": False,
                    "error_code": code,
                    "warning": "Failure is sanitized; a timeout may leave acceptance ambiguous."}
