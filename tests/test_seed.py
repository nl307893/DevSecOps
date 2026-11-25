from uuid import uuid4

import pytest
from flask import Flask
from sqlalchemy import select

from app.database import get_session
from app.models import Comment, Ticket, TicketHistory, User, UserRole
from db.seed import seed_test_data


@pytest.mark.integration
def test_seed_creates_all_entities_idempotently(db_app: Flask) -> None:
    suffix = uuid4()
    client_email = f"seed-client-{suffix}@example.com"
    technician_email = f"seed-technician-{suffix}@example.com"

    with db_app.app_context():
        seed_test_data(
            client_email=client_email,
            client_password="client-password",
            technician_email=technician_email,
            technician_password="technician-password",
        )
        seed_test_data(
            client_email=client_email,
            client_password="client-password",
            technician_email=technician_email,
            technician_password="technician-password",
        )

        session = get_session()
        users = session.scalars(select(User)).all()
        tickets = session.scalars(select(Ticket)).all()
        comments = session.scalars(select(Comment)).all()
        history = session.scalars(select(TicketHistory)).all()

    assert len(users) == 4
    assert sum(1 for user in users if user.role == UserRole.CLIENT) == 2
    assert sum(1 for user in users if user.role == UserRole.TECHNICIAN) == 2
    assert len(tickets) == 3
    assert len(comments) == 3
    assert len(history) == 2
