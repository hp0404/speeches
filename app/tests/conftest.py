import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings
from app.database import get_session
from app.main import app


def get_settings_override():
    """Overrides default get_settings behavior allowing
    testclient to use generic token to authenticate."""
    settings = get_settings()
    settings.SECRET_TOKEN = "foobar"
    return settings


@pytest.fixture(scope="module")
def missing_document():
    """Random valid UUID not found in the database.

    Note: the idea here is to use a valid UUID
    that will not raise an exception on validation
    but will not be found in the database as well.
    """
    return "ab124f2d-1111-1111-1111-a380117c3bb9"


@pytest.fixture(scope="session")
def session():
    """Reusable session."""
    settings = get_settings_override()
    engine = create_engine(str(settings.DATABASE_URI))
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def client(session):
    def get_session_override():
        """Overrides default get_session behavior
        allowing testclient to use a session connected
        to a test database."""
        return session

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_settings] = get_settings_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def sample_data():
    """Generic payload."""
    return [
        {
            "title": "Новость 1",
            "text": "Швеция и Финляндия совместно подали заявку на вступление в НАТО",
            "date": "2022-05-22",
            "URL": "https://sqlmodel.tiangolo.com/",
        },
        {
            "title": "Новость 2",
            "text": "Германия задерживает поставки тяжелого вооружения для Украины",
            "date": "2022-05-22",
            "URL": "https://spacy.io/",
        },
    ]


@pytest.fixture(scope="session")
def uuids(client, sample_data):
    """List of UUIDs that are added to the database on start."""
    # building sample database
    added_uuids = []
    for item in sample_data:
        response = client.post(
            "/speeches/", json=item, headers={"Authorization": "Bearer foobar"}
        )
        added_uuids.append(response.json()["id"])

    # use for GET requests
    yield added_uuids

    # cleaning up
    for uuid in added_uuids:
        response = client.delete(
            f"/speeches/{uuid}", headers={"Authorization": "Bearer foobar"}
        )
