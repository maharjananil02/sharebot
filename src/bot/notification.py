from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def send_email_notification(subject: str, body: str, logger=None) -> bool:
    """Send a simple email notification using SMTP settings from env vars.

    Required env vars: EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_TO
    Returns True on success, False otherwise.
    """
    smtp_server = os.getenv("EMAIL_SMTP")
    smtp_port = os.getenv("EMAIL_PORT")
    smtp_user = os.getenv("EMAIL_USER")
    smtp_pass = os.getenv("EMAIL_PASS")
    email_to = os.getenv("EMAIL_TO")

    if not (smtp_server and smtp_port and smtp_user and smtp_pass and email_to):
        if logger:
            logger.warning(
                "Email settings missing. Set EMAIL_SMTP, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, and EMAIL_TO."
            )
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = email_to
        msg.set_content(body)

        port = int(smtp_port)
        if port == 465:
            with smtplib.SMTP_SSL(smtp_server, port) as smtp:
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, port) as smtp:
                smtp.starttls()
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
        return True
    except Exception as exc:
        if logger:
            logger.exception(f"Email send failed: {exc}")
        return False
