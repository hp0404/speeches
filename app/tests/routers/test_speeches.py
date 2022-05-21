import pytest

DOCUMENT_NOT_FOUND = {"detail": "Document not found"}
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
    """Failed request: the server responds with a validation error on
    invalid input payload."""
    response = client.post(
        "/speeches/", json=sample_data, headers={"Authorization": "Bearer foobar"}
    )
    assert response.status_code == 422
    assert response.json() == VALIDATION_ERROR


def test_create_delete_speeches_success(client, sample_data):
    """Successful request: the client adds two entries and then deletes them."""
    # create
    added_uuids = []
    for item in sample_data:
        response = client.post(
            "/speeches/", json=item, headers={"Authorization": "Bearer foobar"}
        )
        assert response.status_code == 200
        assert "id" in response.json()
        added_uuids.append(response.json()["id"])

    # delete
    for uuid in added_uuids:
        response = client.delete(
            f"/speeches/{uuid}", headers={"Authorization": "Bearer foobar"}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": f"deleted id={uuid}"}


def test_read_speech_by_id_failure(client, missing_document):
    """Failed request: input id is valid but not found (passed validation)."""
    response = client.get(
        f"/speeches/{missing_document}", headers={"Authorization": "Bearer foobar"}
    )
    assert response.status_code == 404
    assert response.json() == DOCUMENT_NOT_FOUND


def test_delete_speech_by_id_failure(client, missing_document):
    """Failed request: input id is valid but not found (passed validation),
    thus it cannot be deleted."""
    response = client.delete(
        f"/speeches/{missing_document}", headers={"Authorization": "Bearer foobar"}
    )
    assert response.status_code == 404
    assert response.json() == DOCUMENT_NOT_FOUND


def test_read_speech_by_id_success(client, uuids):
    """Successful request: input id is valid and found."""
    response = client.get(
        f"/speeches/{uuids[0]}", headers={"Authorization": "Bearer foobar"}
    )
    data = response.json()
    assert len(data) == 6


def test_read_speech_by_id_with_features(client, uuids):
    """Successful request: input id is valid and found, response includes features."""
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


def test_read_speeches(client):
    """Successful request: hidden enpoint responds with metadata's entries"""
    response = client.get("/speeches/", headers={"Authorization": "Bearer foobar"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Новость 1"


def test_read_speeches_offset_limit(client):
    """Successful request: hidden enpoint responds with metadata's entries,
    additional parameters -- offset and limit -- seem to work."""
    response = client.get(
        "/speeches/?offset=1&limit=1", headers={"Authorization": "Bearer foobar"}
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Новость 2"
