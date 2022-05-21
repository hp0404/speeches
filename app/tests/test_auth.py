import pytest

NOT_AUTHENTICATED = {"detail": "Not authenticated"}
INVALID_CREDENTIALS = {"detail": "Invalid authentication credentials"}


def test_auth_success(client):
    """Successfull request with 200 response code."""
    response = client.get(
        "/speeches/",
        headers={"Authorization": "Bearer foobar"},
    )
    assert response.status_code == 200


def test_auth_failure_no_headers(client):
    """Failed request with 'Not authenticated' response:
    no headers are provided."""
    response = client.get("/speeches/")
    assert response.status_code == 401
    assert response.json() == NOT_AUTHENTICATED


@pytest.mark.parametrize("expected_token", ["bar", "foo", ""])
def test_auth_failure_incorrect_token(client, expected_token):
    """Failed request with 'Invalid authentication credentials' response:
    invalid token is provided."""
    response = client.get(
        "/speeches/",
        headers={"Authorization": f"Bearer {expected_token}"},
    )
    assert response.status_code == 401
    assert response.json() == INVALID_CREDENTIALS
