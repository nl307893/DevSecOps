from uuid import UUID

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select

from app.database import get_session
from app.models import Comment, Ticket


@pytest.mark.integration
def test_client_ticket_and_comment_lifecycle(
    db_app: Flask, client: FlaskClient, register_user
) -> None:
    user = register_user()
    headers = user["headers"]

    create_response = client.post(
        "/api/tickets",
        json={
            "title": "Awaria drukarki",
            "description": "Drukarka nie drukuje",
            "category": "hardware",
            "priority": "high",
        },
        headers=headers,
    )
    assert create_response.status_code == 201
    created = create_response.get_json()
    ticket_id = UUID(created["id"])
    assert created["status"] == "new"

    get_response = client.get(f"/api/tickets/{ticket_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.get_json()["title"] == "Awaria drukarki"

    patch_response = client.patch(
        f"/api/tickets/{ticket_id}",
        json={"title": "Zmieniony tytul"},
        headers=headers,
    )
    assert patch_response.status_code == 200
    assert patch_response.get_json()["title"] == "Zmieniony tytul"

    comment_response = client.post(
        f"/api/tickets/{ticket_id}/comments",
        json={"content": "Komentarz klienta"},
        headers=headers,
    )
    assert comment_response.status_code == 201

    with db_app.app_context():
        session = get_session()
        db_ticket = session.get(Ticket, ticket_id)
        assert db_ticket is not None
        assert db_ticket.title == "Zmieniony tytul"
        db_comments = session.scalars(
            select(Comment).where(Comment.ticket_id == ticket_id)
        ).all()
        assert len(db_comments) == 1
        assert db_comments[0].content == "Komentarz klienta"

    delete_response = client.delete(f"/api/tickets/{ticket_id}", headers=headers)
    assert delete_response.status_code == 204

    with db_app.app_context():
        assert get_session().get(Ticket, ticket_id) is None
