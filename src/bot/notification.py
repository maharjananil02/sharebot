from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Optional, List

from dotenv import load_dotenv

load_dotenv()


def _parse_recipients(raw: Optional[str]) -> List[str]:
    """Parse a raw EMAIL_TO string into a list of recipient addresses.

    Accepts comma- or semicolon-separated lists and strips whitespace.
    """
    if not raw:
        return []
    parts = [p.strip() for p in raw.replace(';', ',').split(',')]
    return [p for p in parts if p]


def send_email_notification(subject: str, body: str, logger=None, recipients: Optional[List[str]] = None) -> bool:
    """Send a simple email notification using SMTP settings from env vars.

    Required env vars: EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_TO
    `recipients` may be provided directly (list of addresses). If omitted,
    the `EMAIL_TO` env var will be parsed and used (supports comma/semicolon list).
    Returns True on success, False otherwise.
    """
    smtp_server = os.getenv("EMAIL_SMTP")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_user = os.getenv("EMAIL_USER")
    smtp_pass = os.getenv("EMAIL_PASS")
    email_to = os.getenv("EMAIL_TO")

    if recipients is None:
        recipients = _parse_recipients(email_to)

    if not (smtp_server and smtp_port and smtp_user and smtp_pass and recipients):
        if logger:
            logger.warning(
                "Email settings missing. Set EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, and EMAIL_TO (or pass recipients)."
            )
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)

        port = int(smtp_port)
        if port == 465:
            with smtplib.SMTP_SSL(smtp_server, port) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg, to_addrs=recipients)
        else:
            with smtplib.SMTP(smtp_server, port) as smtp:
                smtp.starttls()
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg, to_addrs=recipients)
        return True
    except Exception as exc:
        if logger:
            logger.exception(f"Email send failed: {exc}")
        return False
