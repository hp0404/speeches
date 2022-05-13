import typing
import logging

import emails
from emails.template import JinjaTemplate
from fastapi import BackgroundTasks, APIRouter

from app.core.config import settings

router = APIRouter(prefix="/send-notification")


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: typing.Dict[str, typing.Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


@router.post("/{email}", include_in_schema=False, response_model=typing.Dict[str, str])
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_email,
        email_to=email,
        subject_template="[{{ proj }}]: Run completed",
        html_template="<p>The database has been updated...</p>",
        environment={"proj": settings.PROJECT_NAME},
    )
    return {"message": "Notification sent in the background"}
