# -*- coding: utf-8 -*-
"""This module contains database engine & session generator."""
import typing

from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URI))


def get_session() -> typing.Iterator[Session]:
    """Yields session"""
    with Session(engine) as session:
        yield session
