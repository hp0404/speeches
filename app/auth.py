# -*- coding: utf-8 -*-
"""This module contains auth dependency.

The app does not assume external users, thus the security worflow
is quite simple: the token is tested against a secret value stored
in the .env file.
"""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def auth_request(token: str = Depends(oauth2_scheme)) -> bool:
    """Verifies token against secret token stored in .env."""
    authenticated = token == settings.SECRET_TOKEN
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authenticated
