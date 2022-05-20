import pytest


def test_auth_success(client):
    """Successfull request with 200 response code."""
    response = client.post(
        "/features/",
        json={"text": "string"},
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.status_code == 200


def test_auth_failure_no_headers(client):
    """'Not authenticated' response when no headers are provided."""
    response = client.post("/features/", json={"text": "string"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.parametrize("expected_token", ["bar", "foo", ""])
def test_auth_failure_incorrect_token(client, expected_token):
    """'Invalid authentication credentials' response when invalid token is provided."""
    response = client.post(
        "/features/",
        json={"text": "string"},
        headers={"Authorization": f"Bearer {expected_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
