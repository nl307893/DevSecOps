from flask import Blueprint, g, jsonify, request
from sqlalchemy import select

from app.auth.decorators import login_required
from app.database import get_session
from app.models import Ticket


tickets_bp = Blueprint("tickets", __name__)

ALLOWED_PRIORITIES = {"low", "medium", "high"}


def _user_id() -> int:
    return int(g.current_user["sub"])


def _is_technician() -> bool:
    return g.current_user["role"] == "technician"


def _serialize(ticket: Ticket) -> dict:
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status.value,
        "client_id": ticket.client_id,
        "technician_id": ticket.technician_id,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }


@tickets_bp.post("")
@login_required
def create_ticket():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    category = str(data.get("category", "")).strip()
    priority = str(data.get("priority", "medium")).strip().lower()

    if not title or not description or not category:
        return jsonify(error="title, description and category are required"), 400
    if len(title) > 255 or len(category) > 100:
        return jsonify(error="title or category too long"), 400
    if priority not in ALLOWED_PRIORITIES:
        return jsonify(error="invalid priority"), 400

    ticket = Ticket(
        title=title,
        description=description,
        category=category,
        priority=priority,
        client_id=_user_id(),
    )
    session = get_session()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return jsonify(_serialize(ticket)), 201


@tickets_bp.get("")
@login_required
def list_tickets():
    query = select(Ticket).order_by(Ticket.created_at.desc())
    if not _is_technician():
        query = query.where(Ticket.client_id == _user_id())
    tickets = get_session().scalars(query).all()
    return jsonify([_serialize(t) for t in tickets])


@tickets_bp.get("/<int:ticket_id>")
@login_required
def get_ticket(ticket_id: int):
    ticket = get_session().get(Ticket, ticket_id)
    if ticket is None:
        return jsonify(error="Ticket not found"), 404
    if not _is_technician() and ticket.client_id != _user_id():
        return jsonify(error="Insufficient permissions"), 403
    return jsonify(_serialize(ticket))