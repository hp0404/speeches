# -*- coding: utf-8 -*-
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def auth_request(token: str = Depends(oauth2_scheme)) -> bool:
    """Using a single secret token to auth one single user.
    This has be to updated once/if we need more users; but
    the rest of the code would work without changes."""
    authenticated = token == settings.SECRET_TOKEN
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return authenticated
