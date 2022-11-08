# -*- coding: utf-8 -*-
"""This module contains database engine & session generator."""
import typing

from fastapi import Depends
from sqlalchemy.future import Engine
from sqlmodel import Session, create_engine

from app.core.config import Settings, get_settings


def get_engine(settings: Settings = Depends(get_settings)):
    """Creates connection engine - used for dependency injection."""
    return create_engine(str(settings.DATABASE_URI))


def get_session(engine: Engine = Depends(get_engine)) -> typing.Iterator[Session]:
    """Yields session."""
    with Session(engine) as session:
        yield session
