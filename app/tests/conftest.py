import pytest
from fastapi.testclient import TestClient
from pydantic import PostgresDsn
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings
from app.database import get_session
from app.main import app


@pytest.fixture(scope="module")
def missing_document():
    """Random valid UUID not found in the database."""
    return "ab124f2d-1111-1111-1111-a380117c3bb9"


@pytest.fixture(scope="session")
def session():
    """
    TODO: build custom settings and replace DB URI instead of building PostgresDsn
    """
    SQLALCHEMY_DATABASE_URL = PostgresDsn.build(
        scheme="postgresql",
        user="postgres",
        password="example",
        host="localhost:5432",
        path="/postgres_test",
    )
    engine = create_engine(str(SQLALCHEMY_DATABASE_URL))
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def client(session):
    def get_session_override():
        return session

    def get_settings_override():
        settings = get_settings()
        settings.SECRET_TOKEN = "foobar"
        return settings

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_settings] = get_settings_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def sample_data():
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
