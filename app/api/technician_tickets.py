from uuid import UUID

from flask import Blueprint, jsonify
from sqlalchemy import select

from app.auth.decorators import roles_required
from app.database import get_session
from app.models import Ticket
from .ticket_helpers import serialize_ticket


technician_tickets_bp = Blueprint("technician_tickets", __name__)


@technician_tickets_bp.get("")
@roles_required("technician")
def list_tickets():
    tickets = get_session().scalars(
        select(Ticket).order_by(Ticket.created_at.desc())
    ).all()
    return jsonify([serialize_ticket(ticket) for ticket in tickets])


@technician_tickets_bp.get("/<uuid:ticket_id>")
@roles_required("technician")
def get_ticket(ticket_id: UUID):
    ticket = get_session().get(Ticket, ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    return jsonify(serialize_ticket(ticket))
