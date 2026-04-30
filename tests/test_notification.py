import unittest
from unittest.mock import MagicMock, patch

from src.bot.notification import send_email_notification


class NotificationTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "EMAIL_SMTP": "smtp.gmail.com",
            "EMAIL_PORT": "465",
            "EMAIL_USER": "user@example.com",
            "EMAIL_PASS": "app-password",
            "EMAIL_TO": "recipient@example.com",
        },
        clear=True,
    )
    @patch("src.bot.notification.smtplib.SMTP_SSL")
    def test_send_email_ssl(self, mock_smtp_ssl):
        smtp_instance = mock_smtp_ssl.return_value.__enter__.return_value
        smtp_instance.login.return_value = None
        smtp_instance.send_message.return_value = None

        result = send_email_notification("Subject", "Body")

        self.assertTrue(result)
        smtp_instance.login.assert_called_once_with("user@example.com", "app-password")
        smtp_instance.send_message.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_settings_returns_false(self):
        self.assertFalse(send_email_notification("Subject", "Body"))


if __name__ == "__main__":
    unittest.main()