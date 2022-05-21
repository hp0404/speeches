import pytest
from app.routers.notifications import send_email

NOTIFICATION = {"detail": "Notification sent in the background"}


@pytest.mark.skip(reason="no way of currently testing this")
def test_send_email():
    ...


def test_send_notification(client, monkeypatch):
    """Sends an email in the background.
    In this context I'm monkeypatching the actual send_email function,
    assuming it works fine, and only verifying the backgroud_tasks'
    response message.
    """

    def send_email_override(*args, **kwargs):
        """Successfull email response attributes."""
        return {
            "success": True,
            "status_code": 250,
            "to_addrs": kwargs["email_to"],
            "from_addr": kwargs["settings"].EMAILS_FROM_EMAIL,
        }

    monkeypatch.setattr("app.routers.notifications.send_email", send_email_override)
    response = client.post(
        "/send-notification/hphcsshtu@gmail.com",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.json() == NOTIFICATION
