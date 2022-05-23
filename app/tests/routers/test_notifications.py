import emails
import pytest

from app.routers.notifications import send_email

EMAIL_TO = "test@gmail.com"
NOTIFICATION = {"detail": "Notification sent in the background"}


class MockMessage:
    """Custom class that will override emails.Message that is being
    called from send_email function."""

    def __init__(self, subject, html, mail_from):
        self.subject = subject
        self.html = html
        self.mail_from = mail_from

    def send(self, to, render, smtp):
        """Overrides emails.backend.response.SMTPResponse."""
        response = emails.backend.response.SMTPResponse()
        response.smtp_options = smtp
        response.to_addrs = [to]
        response.from_addr = self.mail_from
        response.status_code = 250
        response._finished = True
        return response


def test_send_email_success(monkeypatch, settings):
    """Successful request: the message (email) has been sent."""
    monkeypatch.setattr("emails.Message", MockMessage)
    response = send_email(email_to=EMAIL_TO, settings=settings)
    assert response.success
    assert response.to_addrs == [EMAIL_TO]
    assert response.from_addr == (settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)


def test_send_email_emails_disabled_failure(monkeypatch, settings):
    """Failed request: raising AssertionError on EMAILS_ENABLED set to False."""
    monkeypatch.setattr("emails.Message", MockMessage)

    # modifying the copy as settings fixture's scope is set to session
    # meaning 'new' values assigned to settings fixture might influence other tests
    updated_settings = settings.copy()

    # on it's own EMAILS_ENABLED = False doesn't work
    # as settings class runs root_validation that checks if SMTP options are set
    # and updates EMAILS_ENABLED field
    updated_settings.EMAILS_ENABLED = False
    updated_settings.EMAILS_FROM_EMAIL = None
    with pytest.raises(AssertionError):
        send_email(email_to=EMAIL_TO, settings=updated_settings)


@pytest.mark.parametrize(
    "tls,password,expected_response",
    [
        (False, None, ["host", "port", "user"]),
        (True, "example", ["host", "port", "tls", "user", "password"]),
    ],
)
def test_send_email_smtp_options(
    monkeypatch, settings, tls, password, expected_response
):
    """Successful request: send_email function builds smtp_options correctly."""
    monkeypatch.setattr("emails.Message", MockMessage)

    updated_settings = settings.copy()
    updated_settings.SMTP_TLS = tls
    updated_settings.SMTP_PASSWORD = password

    response = send_email(email_to=EMAIL_TO, settings=updated_settings)
    assert list(response.smtp_options.keys()) == expected_response


def test_send_notification(client, monkeypatch):
    """Successful request: background tasks respond with expected message."""
    monkeypatch.setattr("emails.Message", MockMessage)
    response = client.post(
        f"/send-notification/{EMAIL_TO}",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.json() == NOTIFICATION
