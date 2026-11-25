import os
import re

from sqlalchemy import select

from app import create_app
from app.auth.password import hash_password
from app.database import get_session
from app.models import (
    Comment,
    Ticket,
    TicketCategory,
    TicketHistory,
    TicketStatus,
    User,
    UserRole,
)


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _get_or_create_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: UserRole,
) -> User:
    session = get_session()
    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        session.add(user)
        session.flush()
    return user


def seed_demo_users(
    client_email: str,
    client_password: str,
    technician_email: str,
    technician_password: str,
) -> None:
    session = get_session()
    users = (
        (client_email, client_password, "Demo", "Client", UserRole.CLIENT),
        (
            technician_email,
            technician_password,
            "Demo",
            "Technician",
            UserRole.TECHNICIAN,
        ),
    )
    for email, password, first_name, last_name, role in users:
        _get_or_create_user(email, password, first_name, last_name, role)
    session.commit()


def seed_test_data(
    client_email: str,
    client_password: str,
    technician_email: str,
    technician_password: str,
    secondary_client_email: str | None = None,
    secondary_technician_email: str | None = None,
) -> dict[str, list]:
    """Idempotently seed users, tickets, comments, and ticket history for tests."""
    session = get_session()
    client_1 = _get_or_create_user(
        client_email, client_password, "Demo", "Client", UserRole.CLIENT
    )
    technician_1 = _get_or_create_user(
        technician_email,
        technician_password,
        "Demo",
        "Technician",
        UserRole.TECHNICIAN,
    )
    client_2 = _get_or_create_user(
        secondary_client_email or f"second-{client_email}",
        client_password,
        "Anna",
        "Nowak",
        UserRole.CLIENT,
    )
    technician_2 = _get_or_create_user(
        secondary_technician_email or f"second-{technician_email}",
        technician_password,
        "Piotr",
        "Kowalski",
        UserRole.TECHNICIAN,
    )

    ticket_specs = [
        {
            "title": "Awaria drukarki sieciowej",
            "description": "Drukarka na 2. piętrze nie odpowiada na zadania druku.",
            "category": TicketCategory.HARDWARE,
            "priority": "high",
            "status": TicketStatus.NEW,
            "client": client_1,
            "technician": None,
        },
        {
            "title": "Brak dostępu do VPN",
            "description": "Po zmianie hasła klient VPN zgłasza błąd autoryzacji.",
            "category": TicketCategory.ACCESS,
            "priority": "medium",
            "status": TicketStatus.INSTATUS,
            "client": client_1,
            "technician": technician_1,
        },
        {
            "title": "Aktualizacja pakietu biurowego",
            "description": "Prośba o aktualizację oprogramowania na stanowisku.",
            "category": TicketCategory.SOFTWARE,
            "priority": "low",
            "status": TicketStatus.RESOLVED,
            "client": client_2,
            "technician": technician_2,
        },
    ]

    tickets: list[Ticket] = []
    for spec in ticket_specs:
        ticket = session.scalar(
            select(Ticket).where(
                Ticket.client_id == spec["client"].id,
                Ticket.title == spec["title"],
            )
        )
        if ticket is None:
            ticket = Ticket(
                title=spec["title"],
                description=spec["description"],
                category=spec["category"],
                priority=spec["priority"],
                status=spec["status"],
                client_id=spec["client"].id,
                technician_id=(
                    spec["technician"].id if spec["technician"] else None
                ),
            )
            session.add(ticket)
            session.flush()
        tickets.append(ticket)

    comment_specs = [
        (tickets[0], client_1, "Problem występuje od rana."),
        (tickets[1], technician_1, "Sprawdzam logi serwera VPN."),
        (tickets[2], technician_2, "Aktualizacja zakończona pomyślnie."),
    ]
    comments: list[Comment] = []
    for ticket, author, content in comment_specs:
        comment = session.scalar(
            select(Comment).where(
                Comment.ticket_id == ticket.id,
                Comment.author_id == author.id,
                Comment.content == content,
            )
        )
        if comment is None:
            comment = Comment(
                ticket_id=ticket.id,
                author_id=author.id,
                content=content,
            )
            session.add(comment)
            session.flush()
        comments.append(comment)

    history_specs = [
        (tickets[1], TicketStatus.NEW, TicketStatus.INSTATUS, technician_1),
        (tickets[2], TicketStatus.NEW, TicketStatus.RESOLVED, technician_2),
    ]
    history_entries: list[TicketHistory] = []
    for ticket, old_status, new_status, actor in history_specs:
        entry = session.scalar(
            select(TicketHistory).where(
                TicketHistory.ticket_id == ticket.id,
                TicketHistory.old_status == old_status,
                TicketHistory.new_status == new_status,
            )
        )
        if entry is None:
            entry = TicketHistory(
                ticket_id=ticket.id,
                old_status=old_status,
                new_status=new_status,
                changed_by=actor.id,
            )
            session.add(entry)
            session.flush()
        history_entries.append(entry)

    session.commit()
    return {
        "users": [client_1, technician_1, client_2, technician_2],
        "tickets": tickets,
        "comments": comments,
        "history": history_entries,
    }


def main() -> None:
    if os.getenv("SEED_DEMO_DATA") != "1":
        raise RuntimeError(
            "Set SEED_DEMO_DATA=1 to explicitly enable demo seeding"
        )

    values = {
        "client_email": os.getenv("SEED_CLIENT_EMAIL"),
        "client_password": os.getenv("SEED_CLIENT_PASSWORD"),
        "technician_email": os.getenv("SEED_TECHNICIAN_EMAIL"),
        "technician_password": os.getenv("SEED_TECHNICIAN_PASSWORD"),
    }
    if any(value is None for value in values.values()):
        raise RuntimeError(
            "Set all SEED_CLIENT_* and SEED_TECHNICIAN_* variables"
        )
    if not all(EMAIL_PATTERN.fullmatch(values[key]) for key in (
        "client_email",
        "technician_email",
    )):
        raise RuntimeError("Seed email variables must contain valid emails")

    app = create_app()
    with app.app_context():
        seed_test_data(**values)
    print("Demo users and sample entities are ready.")


if __name__ == "__main__":
    main()
