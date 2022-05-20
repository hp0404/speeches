import pytest

VALIDATION_ERROR = {
    "detail": [
        {
            "loc": ["body", "title"],
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ["body", "text"],
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ["body", "date"],
            "msg": "field required",
            "type": "value_error.missing",
        },
        {
            "loc": ["body", "URL"],
            "msg": "field required",
            "type": "value_error.missing",
        },
    ]
}


def test_create_speeches_failure(client, sample_data):
    """Fail when passing list of elements."""
    response = client.post(
        "/speeches/", json=sample_data, headers={"Authorization": "Bearer foobar"}
    )
    assert response.status_code == 422
    assert response.json() == VALIDATION_ERROR


def test_create_speeches_success(client, sample_data):
    """Proper create_speeches test, but it creates +2 entries besides pytest.fixture;
    somehow need to fix it, for now it's the last test so it doesn't change much.
    """
    for item in sample_data:
        response = client.post(
            "/speeches/", json=item, headers={"Authorization": "Bearer foobar"}
        )
        assert response.status_code == 200
        assert response.json() == {"ok": True}


def test_read_speeches(client):
    """Read all speeches from a hidden endpoint."""
    response = client.get("/speeches/", headers={"Authorization": "Bearer foobar"})
    assert response.status_code == 200
    data = response.json()
    # assert len(data) == 2
    assert data[0]["title"] == "Новость 1"


def test_read_speeches_offset_limit(client):
    """Read speeches using offset & limit params."""
    response = client.get(
        "/speeches/?offset=1&limit=1", headers={"Authorization": "Bearer foobar"}
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Новость 2"


def test_read_speech_by_id(client, uuids):
    """Read document by id."""
    response = client.get(
        f"/speeches/{uuids[0]}", headers={"Authorization": "Bearer foobar"}
    )
    data = response.json()
    assert len(data) == 6


def test_read_speech_by_id_with_features(client, uuids):
    """Read document by id including features."""
    response = client.get(
        f"/speeches/{uuids[1]}?include_features=true",
        headers={"Authorization": "Bearer foobar"},
    )
    data = response.json()
    assert list(data.keys()) == [
        "id",
        "created_at",
        "date",
        "title",
        "URL",
        "text",
        "features",
    ]
    assert len(data["features"]) == 3
    assert data["features"][-1]["feature_label"] == "ADJ-NOUN"
    assert (
        data["text"] == "Германия задерживает поставки тяжелого вооружения для Украины"
    )
