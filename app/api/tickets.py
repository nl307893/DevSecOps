from uuid import UUID

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.auth.decorators import login_required
from app.database import get_session
from app.models import Ticket
from .ticket_helpers import current_user_id, serialize_ticket


tickets_bp = Blueprint("tickets", __name__)

ALLOWED_PRIORITIES = {"low", "medium", "high"}


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
        client_id=current_user_id(),
    )
    session = get_session()
    session.add(ticket)
    session.commit()
    session.refresh(ticket)
    return jsonify(serialize_ticket(ticket)), 201


@tickets_bp.get("")
@login_required
def list_tickets():
    query = (
        select(Ticket)
        .where(Ticket.client_id == current_user_id())
        .order_by(Ticket.created_at.desc())
    )
    tickets = get_session().scalars(query).all()
    return jsonify([serialize_ticket(ticket) for ticket in tickets])


@tickets_bp.get("/<uuid:ticket_id>")
@login_required
def get_ticket(ticket_id: UUID):
    ticket = get_session().scalar(
        select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.client_id == current_user_id(),
        )
    )
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    return jsonify(serialize_ticket(ticket))