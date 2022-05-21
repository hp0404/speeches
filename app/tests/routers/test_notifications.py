import pytest
import emails

from app.core.config import get_settings
from app.routers.notifications import send_email

EMAIL_TO = "test@gmail.com"
NOTIFICATION = {"detail": "Notification sent in the background"}


class MockMessage:
    """Custom class that will override emails.Message
    called from send_email function."""

    def __init__(self, subject, html, mail_from):
        self.subject = subject
        self.html = html
        self.mail_from = mail_from

    def send(self, to, render, smtp):
        """Send method that will override emails.backend.response.SMTPResponse."""
        response = emails.backend.response.SMTPResponse()
        response.smtp_options = smtp
        response.to_addrs = [to]
        response.from_addr = self.mail_from
        response.status_code = 250
        response._finished = True
        return response


def test_send_email_success(monkeypatch):
    """Send mail successfully."""
    monkeypatch.setattr("emails.Message", MockMessage)
    settings = get_settings()
    response = send_email(email_to=EMAIL_TO, settings=settings)
    assert response.success
    assert response.to_addrs == [EMAIL_TO]
    assert response.from_addr == (settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)


def test_send_email_emails_disabled_failure():
    """Make sure send_email raises AssertionError when
    EMAILS_ENABLED is set to False"""
    settings = get_settings()
    settings.EMAILS_ENABLED = False
    with pytest.raises(AssertionError):
        send_email(email_to=EMAIL_TO, settings=settings)


@pytest.mark.parametrize(
    "tls,password,expected_response",
    [
        (False, False, ["host", "port", "user"]),
        (True, True, ["host", "port", "tls", "user", "password"]),
    ],
)
def test_send_email_smtp_options(monkeypatch, tls, password, expected_response):
    """Make sure the function builds smtp_options correctly."""
    monkeypatch.setattr("emails.Message", MockMessage)

    settings = get_settings()
    settings.SMTP_TLS = tls
    settings.SMTP_PASSWORD = password

    response = send_email(email_to=EMAIL_TO, settings=settings)
    assert list(response.smtp_options.keys()) == expected_response


def test_send_notification(client, monkeypatch):
    """Sends an email in the background."""
    monkeypatch.setattr("emails.Message", MockMessage)
    response = client.post(
        f"/send-notification/{EMAIL_TO}",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.json() == NOTIFICATION
