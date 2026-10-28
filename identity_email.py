"""Configurable SMTP delivery for one-time identity lifecycle messages.

This module intentionally never logs message bodies, recipients, tokens, or credentials.
Production callers must configure an explicit public HTTPS origin in the application.
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage


class IdentityEmailError(RuntimeError):
    """Raised when secure identity-email delivery is unavailable."""


def send_identity_email(recipient: str, subject: str, body: str) -> None:
    recipient = str(recipient).strip()
    if not recipient or any(char in recipient for char in "\r\n"):
        raise IdentityEmailError("recipient address is invalid")
    if not subject or any(char in subject for char in "\r\n"):
        raise IdentityEmailError("message subject is invalid")
    host = os.environ.get("COPILOT_EMAIL_SMTP_HOST", "").strip()
    sender = os.environ.get("COPILOT_EMAIL_FROM", "").strip()
    if not host or not sender or any(char in sender for char in "\r\n"):
        raise IdentityEmailError("SMTP host and sender must be configured")
    try:
        port = int(os.environ.get("COPILOT_EMAIL_SMTP_PORT", "587"))
    except ValueError as exc:
        raise IdentityEmailError("SMTP port configuration is invalid") from exc
    if not 1 <= port <= 65535:
        raise IdentityEmailError("SMTP port configuration is invalid")
    security = os.environ.get("COPILOT_EMAIL_SMTP_SECURITY", "starttls").strip().lower()
    production = os.environ.get("COPILOT_ENV", "").strip().lower() in {"prod", "production"}
    if security not in {"starttls", "ssl", "plain"}:
        raise IdentityEmailError("SMTP transport security must be starttls, ssl, or plain")
    if production and security == "plain":
        raise IdentityEmailError("unencrypted SMTP is disabled in production")
    username = os.environ.get("COPILOT_EMAIL_SMTP_USERNAME", "").strip()
    password = os.environ.get("COPILOT_EMAIL_SMTP_PASSWORD", "")
    if bool(username) != bool(password):
        raise IdentityEmailError("SMTP username and password must be configured together")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    timeout = 10
    context = ssl.create_default_context()
    try:
        if security == "ssl":
            with smtplib.SMTP_SSL(host, port, timeout=timeout, context=context) as server:
                if username:
                    server.login(username, password)
                server.send_message(message)
        else:
            with smtplib.SMTP(host, port, timeout=timeout) as server:
                server.ehlo()
                if security == "starttls":
                    server.starttls(context=context)
                    server.ehlo()
                if username:
                    server.login(username, password)
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise IdentityEmailError("identity email delivery failed") from exc
