# -*- coding: utf-8 -*-
"""This module contains /send-notification/ router."""
import logging
import typing

import emails  # type: ignore
from emails.template import JinjaTemplate  # type: ignore
from fastapi import APIRouter, BackgroundTasks, Depends

from app.core.config import Settings, get_settings

router = APIRouter(prefix="/send-notification")


def send_email(
    email_to: str,
    settings: Settings,
    subject_template: str = "",
    html_template: str = "",
    environment: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> None:
    """Generic utility function that builds and sends template messages."""
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
    response = message.send(to=email_to, render=environment or {}, smtp=smtp_options)
    logging.info(f"send email result: {response}")  # pylint: disable=logging-fstring-interpolation


@router.post(
    "/{email}",
    include_in_schema=False,
    response_model=typing.Dict[str, str],
)
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
):
    """Sends generic message updating on the status of cronjob workflow."""
    background_tasks.add_task(
        send_email,
        settings=settings,
        email_to=email,
        subject_template="[{{ proj }}]: Run completed",
        html_template="<p>The database has been updated...</p>",
        environment={"proj": settings.PROJECT_NAME},
    )
    return {"message": "Notification sent in the background"}
