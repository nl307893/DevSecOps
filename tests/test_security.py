from uuid import UUID

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.database import get_session
from app.models import Ticket


@pytest.mark.security
def test_user_cannot_modify_delete_or_access_other_users_or_technician_resources(
    db_app: Flask, client: FlaskClient, register_user
) -> None:
    owner = register_user()
    attacker = register_user()

    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Poufne zgloszenie",
            "description": "Szczegoly problemu",
            "category": "access",
            "priority": "high",
        },
        headers=owner["headers"],
    )
    assert create_response.status_code == 201
    ticket_id = UUID(create_response.get_json()["id"])

    patch_response = client.patch(
        f"/api/tickets/{ticket_id}",
        json={"title": "Nieautoryzowana zmiana"},
        headers=attacker["headers"],
    )
    delete_response = client.delete(
        f"/api/tickets/{ticket_id}",
        headers=attacker["headers"],
    )
    tech_response = client.get(
        "/api/technician/tickets",
        headers=attacker["headers"],
    )

    assert patch_response.status_code == 404
    assert delete_response.status_code == 404
    assert tech_response.status_code == 404

    with db_app.app_context():
        ticket = get_session().get(Ticket, ticket_id)
        assert ticket is not None
        assert ticket.title == "Poufne zgloszenie"


@pytest.mark.security
def test_password_length_policy_enforced_on_register_and_password_change(
    client: FlaskClient, register_user
) -> None:
    short_register_response = client.post(
        "/api/auth/register",
        json={"email": "short-pass@example.com", "password": "short"},
    )
    assert short_register_response.status_code == 400
    assert "at least 12 characters" in short_register_response.get_json()["error"]

    user = register_user(password="valid-long-password")
    short_change_response = client.patch(
        "/api/users/me/password",
        json={
            "current_password": user["password"],
            "new_password": "1234567",
        },
        headers=user["headers"],
    )
    assert short_change_response.status_code == 400
    assert "at least 8 characters" in short_change_response.get_json()["error"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200
