# -*- coding: utf-8 -*-
"""This module contains BaseSettings config."""
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings, EmailStr, PostgresDsn, root_validator, validator


class Settings(BaseSettings):
    """Defines base settings of the app."""

    PROJECT_NAME: str
    DESCRIPTION: str
    SECRET_TOKEN: str
    # workaround for environment variables
    # https://github.com/samuelcolvin/pydantic/issues/1458#issuecomment-789051576
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Optional[PostgresDsn] = None

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[Union[str, EmailStr]] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAILS_ENABLED: bool = False

    @root_validator
    def assemble_db_connection_and_get_emails_enabled(
        cls, values: Dict[str, Any]
    ) -> Any:
        values["DATABASE_URI"] = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
        values["EMAILS_ENABLED"] = bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )
        return values

    class Config:
        validate_assignment = True
        case_sensitive = True
        env_file = ".env"


def get_settings() -> Settings:
    """Creates settings - used for dependency injection."""
    return Settings()
