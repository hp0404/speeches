import pytest
from app.database import get_engine, get_session


def test_get_engine(settings):
    """Successful engine creation."""
    engine = get_engine(settings)
    assert engine.name == "postgresql"

    host, port = settings.POSTGRES_SERVER.split(":")
    assert engine.url.host == host
    assert engine.url.port == int(port)
    assert engine.url.username == settings.POSTGRES_USER
    assert engine.url.password == settings.POSTGRES_PASSWORD
    assert engine.url.database == settings.POSTGRES_DB


def test_get_session(settings):
    """Successful connection."""
    engine = get_engine(settings)
    session = get_session(engine)
    assert next(session).connection()
