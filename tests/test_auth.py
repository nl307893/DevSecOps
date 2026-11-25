from uuid import uuid4

import bcrypt
import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from app.database import get_session
from app.models import User


@pytest.mark.integration
def test_register_user_with_valid_email_persists_hashed_password(
    db_app: Flask, client: FlaskClient
) -> None:
    email = f"valid-{uuid4()}@example.com"
    password = "correct-password"

    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )

    assert response.status_code == 201
    tokens = response.get_json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "Bearer"

    with db_app.app_context():
        user = get_session().scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.password_hash != password
        assert bcrypt.checkpw(password.encode(), user.password_hash.encode())


@pytest.mark.integration
def test_register_user_with_invalid_email_is_rejected_and_not_saved(
    db_app: Flask, client: FlaskClient
) -> None:
    response = client.post(
        "/api/auth/register",
        json={"email": "invalid-email", "password": "correct-password"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid email"}

    with db_app.app_context():
        users = get_session().scalars(select(User)).all()
        assert users == []


@pytest.mark.integration
def test_login_refresh_and_logout_session_lifecycle(
    client: FlaskClient, register_user
) -> None:
    user = register_user()

    login_response = client.post(
        "/api/auth/login",
        json={"email": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200
    login_tokens = login_response.get_json()

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed_tokens = refresh_response.get_json()
    assert refreshed_tokens["refresh_token"] != login_tokens["refresh_token"]

    reused_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert reused_response.status_code == 401

    logout_response = client.post(
        "/api/auth/logout",
        json={"refresh_token": refreshed_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 204

    after_logout_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refreshed_tokens["refresh_token"]},
    )
    assert after_logout_response.status_code == 401
