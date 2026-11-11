from uuid import UUID

from flask import g

from app.models import Ticket


def current_user_id() -> UUID:
    return UUID(g.current_user["sub"])


def serialize_ticket(ticket: Ticket) -> dict:
    return {
        "id": str(ticket.id),
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category.value,
        "priority": ticket.priority,
        "status": ticket.status.value,
        "client_id": str(ticket.client_id),
        "technician_id": (
            str(ticket.technician_id) if ticket.technician_id else None
        ),
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }
