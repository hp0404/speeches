import pytest

VALIDATION_ERROR = {
    "detail": [
        {
            "loc": ["path", "document_id"],
            "msg": "value is not a valid uuid",
            "type": "type_error.uuid",
        }
    ]
}


@pytest.mark.parametrize(
    "invalid_id,expected_status,expected_response",
    [
        ("", 405, {"detail": "Method Not Allowed"}),
        ("first_document", 422, VALIDATION_ERROR),
        (1, 422, VALIDATION_ERROR),
    ],
)
def test_read_features_by_document_invalid_uuid(
    client, invalid_id, expected_status, expected_response
):
    """Input id is invalid."""
    response = client.get(
        f"/features/{invalid_id}",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response


def test_read_features_by_document_document_not_found(client):
    """Document not found."""
    response = client.get(
        "/features/ab124f2d-e627-49fd-1111-a380117c3bb9",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_read_features_by_document_document_found(client, uuids):
    """Document was found."""
    response = client.get(
        f"/features/{uuids[1]}", headers={"Authorization": "Bearer foobar"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 3
    # the request returned both NP and NE types
    assert any(item["feature_type"] == "NP" for item in response.json())
    assert any(item["feature_type"] == "NE" for item in response.json())


def test_read_features_by_document_document_found_limit_success(client, uuids):
    """Document was found, successfully limited feature types to NE."""
    response = client.get(
        f"/features/{uuids[1]}?feature_type=NE",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    # the request returned only NE types
    assert all(item["feature_type"] == "NE" for item in response.json())


def test_read_features_by_document_document_found_limit_failure(client, uuids):
    """Document was found, but there were no features accossiated with it."""
    response = client.get(
        f"/features/{uuids[0]}?feature_type=NP",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


@pytest.mark.parametrize(
    "payload,expected_response",
    [
        (
            {"text": "Швеция и Финляндия совместно подали заявку на вступление в НАТО"},
            [
                {
                    "feature_type": "NE",
                    "feature_label": "LOC",
                    "match": "Швеция",
                    "match_normalized": "швеция",
                    "location": [0, 6],
                },
                {
                    "feature_type": "NE",
                    "feature_label": "LOC",
                    "match": "Финляндия",
                    "match_normalized": "финляндия",
                    "location": [9, 18],
                },
                {
                    "feature_type": "NE",
                    "feature_label": "ORG",
                    "match": "НАТО",
                    "match_normalized": "нато",
                    "location": [59, 63],
                },
            ],
        ),
        (
            {"text": "Германия задерживает поставки тяжелого вооружения для Украины"},
            [
                {
                    "feature_type": "NE",
                    "feature_label": "LOC",
                    "match": "Германия",
                    "match_normalized": "германия",
                    "location": [0, 8],
                },
                {
                    "feature_type": "NE",
                    "feature_label": "LOC",
                    "match": "Украины",
                    "match_normalized": "украина",
                    "location": [54, 61],
                },
                {
                    "feature_type": "NP",
                    "feature_label": "ADJ-NOUN",
                    "match": "тяжелого вооружения",
                    "match_normalized": "тяжёлый вооружение",
                    "location": [30, 49],
                },
            ],
        ),
    ],
)
def test_extract_features_from_text(client, payload, expected_response):
    """Test ML"""
    response = client.post(
        "/features/", json=payload, headers={"Authorization": "Bearer foobar"}
    )
    assert response.json() == expected_response
