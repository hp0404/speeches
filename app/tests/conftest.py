import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app.core.config import get_settings
from app.database import get_engine, get_session
from app.main import app


@pytest.fixture(scope="module")
def missing_document():
    """Random valid UUID not found in the database.

    Note: the idea here is to use a valid UUID
    that will not raise an exception on validation
    but will not be found in the database as well.
    """
    return "ab124f2d-1111-1111-1111-a380117c3bb9"


@pytest.fixture(scope="session")
def settings():
    """Base settings class adjusted for testing purposes."""
    # for local testing, change fields according to your needs
    # since we're using github actions CI, we already have our env variables
    # set to test database, so in this commit I'm keeping default settings values
    settings = get_settings()
    settings.SECRET_TOKEN = "foobar"
    settings.EMAILS_FROM_NAME = "bot"

    # # test database
    # settings.POSTGRES_SERVER = ""
    # settings.POSTGRES_USER = ""
    # settings.POSTGRES_PASSWORD = ""
    # settings.POSTGRES_DB = "postgres_test"
    return settings


@pytest.fixture(scope="session")
def session(settings):
    """Reusable session."""
    engine = get_engine(settings)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def client(session, settings):
    """Reusable client."""

    def get_settings_override():
        """Overrides default get_settings behavior."""
        return settings

    def get_session_override():
        """Overrides default get_session behavior."""
        return session

    app.dependency_overrides[get_settings] = get_settings_override
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def sample_data():
    """Generic payload."""
    return [
        {
            "title": "?????????????? 1",
            "text": "???????????? ?? ?????????????????? ?????????????????? ???????????? ???????????? ???? ???????????????????? ?? ????????",
            "date": "2022-05-22",
            "URL": "https://sqlmodel.tiangolo.com/",
        },
        {
            "title": "?????????????? 2",
            "text": "???????????????? ?????????????????????? ???????????????? ???????????????? ???????????????????? ?????? ??????????????",
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
