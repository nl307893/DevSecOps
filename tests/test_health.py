import pytest
from flask.testing import FlaskClient


@pytest.mark.smoke
def test_health_returns_ok_without_login(unit_client: FlaskClient) -> None:
    response = unit_client.get("/api/health")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert response.get_json() == {"status": "ok"}
