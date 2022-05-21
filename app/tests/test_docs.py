import pytest


def test_docs_redirect(client):
    """Root endpoint redirects to /docs by default."""
    response = client.get("/")
    assert response.history[0].status_code == 307
    assert response.status_code == 200
    assert response.url == "http://testserver/docs"
