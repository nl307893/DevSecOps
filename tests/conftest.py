from collections.abc import Callable, Generator
from uuid import uuid4

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer

from app import create_app
from app.database import get_session


def _normalize_postgres_url(url: str) -> str:
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    """Start a single PostgreSQL 17 container for the entire test session."""
    with PostgresContainer("postgres:17-alpine") as container:
        url = _normalize_postgres_url(container.get_connection_url())
        app = create_app(
            {
                "TESTING": True,
                "DATABASE_URL": url,
                "INIT_DB": True,
                "SECRET_KEY": "integration-test-secret",
            }
        )
        assert app is not None
        yield url


@pytest.fixture
def unit_app() -> Flask:
    """Create a Flask application without initializing a database."""
    return create_app(
        {
            "TESTING": True,
            "INIT_DB": False,
            "DATABASE_URL": "postgresql://unused",
            "SECRET_KEY": "unit-test-secret",
        }
    )


@pytest.fixture
def unit_client(unit_app: Flask) -> FlaskClient:
    return unit_app.test_client()


@pytest.fixture
def db_app(postgres_url: str) -> Generator[Flask, None, None]:
    """Provide an isolated Flask app backed by a clean PostgreSQL database."""
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": postgres_url,
            "INIT_DB": False,
            "SECRET_KEY": "integration-test-secret",
        }
    )
    with app.app_context():
        session = get_session()
        session.execute(
            text(
                "TRUNCATE TABLE refresh_tokens, ticket_history, comments, tickets, users "
                "RESTART IDENTITY CASCADE"
            )
        )
        session.commit()
    yield app
    with app.app_context():
        session = get_session()
        session.execute(
            text(
                "TRUNCATE TABLE refresh_tokens, ticket_history, comments, tickets, users "
                "RESTART IDENTITY CASCADE"
            )
        )
        session.commit()


@pytest.fixture
def client(db_app: Flask) -> FlaskClient:
    return db_app.test_client()


@pytest.fixture
def register_user(client: FlaskClient) -> Callable[..., dict]:
    """Register a client user via API and return auth headers and credentials."""

    def _register(
        email: str | None = None,
        password: str = "correct-password",
    ) -> dict:
        user_email = email or f"{uuid4()}@example.com"
        response = client.post(
            "/api/auth/register",
            json={"email": user_email, "password": password},
        )
        assert response.status_code == 201
        tokens = response.get_json()
        return {
            "email": user_email,
            "password": password,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "headers": {"Authorization": f"Bearer {tokens['access_token']}"},
        }

    return _register
