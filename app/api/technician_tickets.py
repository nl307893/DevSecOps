from uuid import UUID

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.auth.decorators import roles_required
from app.database import get_session
from app.models import (
    Ticket,
    TicketCategory,
    TicketHistory,
    TicketStatus,
    User,
    UserRole,
)
from .ticket_helpers import current_user_id, serialize_ticket


technician_tickets_bp = Blueprint("technician_tickets", __name__)
ALLOWED_PRIORITIES = {"low", "medium", "high"}


def _get_ticket(ticket_id: UUID) -> Ticket | None:
    return get_session().get(Ticket, ticket_id)


def _json_object() -> dict | None:
    data = request.get_json(silent=True) or {}
    return data if isinstance(data, dict) else None


def _record_status_change(
    ticket: Ticket, old_status: TicketStatus
) -> None:
    if ticket.status == old_status:
        return
    get_session().add(
        TicketHistory(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=ticket.status,
            changed_by=current_user_id(),
        )
    )


@technician_tickets_bp.get("")
@roles_required("technician")
def list_tickets():
    tickets = get_session().scalars(
        select(Ticket).order_by(Ticket.created_at.desc())
    ).all()
    return jsonify(
        [serialize_ticket(ticket, include_priority=True) for ticket in tickets]
    )


@technician_tickets_bp.get("/<uuid:ticket_id>")
@roles_required("technician")
def get_ticket(ticket_id: UUID):
    ticket = _get_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    return jsonify(serialize_ticket(ticket, include_priority=True))


@technician_tickets_bp.patch("/<uuid:ticket_id>/priority")
@roles_required("technician")
def update_priority(ticket_id: UUID):
    ticket = _get_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    data = _json_object()
    priority = data.get("priority") if data else None
    if (
        not isinstance(priority, str)
        or priority.strip().lower() not in ALLOWED_PRIORITIES
    ):
        return jsonify(error="invalid priority"), 400

    ticket.priority = priority.strip().lower()
    get_session().commit()
    get_session().refresh(ticket)
    return jsonify(serialize_ticket(ticket, include_priority=True))


@technician_tickets_bp.patch("/<uuid:ticket_id>/assign")
@roles_required("technician")
def assign_technician(ticket_id: UUID):
    ticket = _get_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    data = _json_object()
    if data is None:
        return jsonify(error="request body must be an object"), 400
    raw_technician_id = data.get("technician_id", str(current_user_id()))
    if raw_technician_id is None:
        ticket.technician_id = None
    elif isinstance(raw_technician_id, str):
        try:
            technician_id = UUID(raw_technician_id)
        except ValueError:
            return jsonify(error="invalid technician_id"), 400
        technician = get_session().get(User, technician_id)
        if technician is None or technician.role != UserRole.TECHNICIAN:
            return jsonify(error="Resource not found"), 404
        ticket.technician_id = technician_id
        old_status = ticket.status
        if technician_id == current_user_id():
            ticket.status = TicketStatus.INSTATUS
            _record_status_change(ticket, old_status)
    else:
        return jsonify(error="invalid technician_id"), 400

    get_session().commit()
    get_session().refresh(ticket)
    return jsonify(serialize_ticket(ticket, include_priority=True))


@technician_tickets_bp.patch("/<uuid:ticket_id>/status")
@roles_required("technician")
def update_status(ticket_id: UUID):
    ticket = _get_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    data = _json_object()
    if data is None:
        return jsonify(error="request body must be an object"), 400
    raw_status = data.get("status") if data else None
    if not isinstance(raw_status, str):
        return jsonify(error="status is required"), 400
    try:
        new_status = TicketStatus(raw_status.strip().lower())
    except ValueError:
        return jsonify(error="invalid status"), 400

    old_status = ticket.status
    ticket.status = new_status
    _record_status_change(ticket, old_status)
    get_session().commit()
    get_session().refresh(ticket)
    return jsonify(serialize_ticket(ticket, include_priority=True))


@technician_tickets_bp.patch("/<uuid:ticket_id>/category")
@roles_required("technician")
def update_category(ticket_id: UUID):
    ticket = _get_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    data = _json_object()
    if data is None:
        return jsonify(error="request body must be an object"), 400
    raw_category = data.get("category") if data else None
    if not isinstance(raw_category, str):
        return jsonify(error="category is required"), 400
    try:
        ticket.category = TicketCategory(raw_category.strip().lower())
    except ValueError:
        return jsonify(error="invalid category"), 400

    get_session().commit()
    get_session().refresh(ticket)
    return jsonify(serialize_ticket(ticket, include_priority=True))
