# -*- coding: utf-8 -*-
"""This module contains auth_request dependency.

We assume the access would be limited to HCSS users, thus the security worflow
is simplified to checking if provided token matches the secret value stored in
.env file.
"""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.core.config import Settings, get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def auth_request(
    token: str = Depends(oauth2_scheme), settings: Settings = Depends(get_settings)
) -> bool:
    """Verifies token against secret token stored in .env."""
    authenticated = token == settings.SECRET_TOKEN
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authenticated
