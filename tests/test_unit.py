from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import jwt
import pytest
from flask import Flask

from app.api.Client.tickets import _ticket_data
from app.api.ticket_helpers import validate_comment_content
from app.auth.decorators import login_required
from app.auth.password import hash_password, verify_password
from app.auth.service import create_refresh_token


@pytest.mark.unit
def test_hash_password_can_be_verified() -> None:
    password_hash = hash_password("correct-password")

    assert password_hash != "correct-password"
    assert verify_password("correct-password", password_hash) is True


@pytest.mark.unit
def test_verify_password_rejects_wrong_password() -> None:
    password_hash = hash_password("correct-password")

    assert verify_password("wrong-password", password_hash) is False


@pytest.mark.unit
def test_ticket_data_normalizes_valid_values() -> None:
    values, error = _ticket_data(
        {
            "title": "  Awaria drukarki ",
            "description": "  Nie drukuje ",
            "category": " HARDWARE ",
            "priority": " HIGH ",
        }
    )

    assert error is None
    assert values == {
        "title": "Awaria drukarki",
        "description": "Nie drukuje",
        "category": "hardware",
        "priority": "high",
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        ({"title": "Title"}, "title, description and category are required"),
        (
            {
                "title": "Title",
                "description": "Description",
                "category": "hardware",
                "priority": "urgent",
            },
            "invalid priority",
        ),
        (
            {
                "title": "Title",
                "description": "Description",
                "category": "unknown",
                "priority": "high",
            },
            "invalid category",
        ),
    ],
)
def test_ticket_data_rejects_invalid_input(
    payload: dict, expected_error: str
) -> None:
    values, error = _ticket_data(payload)

    assert values == {}
    assert error == expected_error


@pytest.mark.unit
def test_validate_comment_content_strips_surrounding_whitespace() -> None:
    content, error = validate_comment_content("  Problem nadal wystepuje  ")

    assert content == "Problem nadal wystepuje"
    assert error is None


@pytest.mark.unit
@pytest.mark.parametrize(
    ("raw_content", "expected_error"),
    [
        (None, "content is required"),
        ("   ", "content cannot be empty"),
        ("a" * 5001, "content too long"),
    ],
)
def test_validate_comment_content_rejects_invalid_values(
    raw_content: object, expected_error: str
) -> None:
    content, error = validate_comment_content(raw_content)

    assert content is None
    assert error == expected_error


@pytest.mark.unit
def test_create_refresh_token_uses_session_and_persists_token(
    unit_app: Flask,
) -> None:
    user_id = uuid4()
    session = Mock()

    with (
        unit_app.app_context(),
        patch("app.auth.service.get_session", return_value=session),
        patch(
            "app.auth.service.secrets.token_urlsafe",
            return_value="refresh-token",
        ),
    ):
        token = create_refresh_token(user_id)

    refresh_token = session.add.call_args.args[0]
    assert token == "refresh-token"
    assert refresh_token.user_id == user_id
    assert refresh_token.expires_at is not None
    session.commit.assert_called_once_with()


@pytest.mark.unit
@pytest.mark.parametrize(
    ("secret", "exp_delta"),
    [
        ("unit-test-secret", timedelta(minutes=-1)),
        ("wrong-unit-test-secret", timedelta(minutes=15)),
    ],
)
def test_login_required_rejects_expired_or_invalid_signature_token(
    unit_app: Flask, secret: str, exp_delta: timedelta
) -> None:
    @login_required
    def protected_view():
        return "protected"

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "client",
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(minutes=30),
            "exp": datetime.now(timezone.utc) + exp_delta,
        },
        secret,
        algorithm="HS256",
    )

    with unit_app.test_request_context(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    ):
        response, status_code = protected_view()

    assert status_code == 401
    assert "error" in response.get_json()
