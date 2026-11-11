from uuid import UUID

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from app.auth.decorators import login_required
from app.database import get_session
from app.models import Comment, Ticket, TicketCategory, TicketStatus
from ..ticket_helpers import (
    current_user_id,
    serialize_comment,
    serialize_ticket,
    validate_comment_content,
)


tickets_bp = Blueprint("tickets", __name__)

ALLOWED_PRIORITIES = {"low", "medium", "high"}
ALLOWED_CATEGORIES = {category.value for category in TicketCategory}


def _get_owned_ticket(ticket_id: UUID, lock: bool = False) -> Ticket | None:
    query = select(Ticket).where(
            Ticket.id == ticket_id,
            Ticket.client_id == current_user_id(),
        )
    if lock:
        query = query.with_for_update()
    return get_session().scalar(query)


def _ticket_data(data: dict, partial: bool = False) -> tuple[dict, str | None]:
    fields = ("title", "description", "category", "priority")
    if partial and not any(field in data for field in fields):
        return {}, "at least one ticket field is required"

    if partial:
        values = {field: data[field] for field in fields if field in data}
    else:
        values = {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "category": data.get("category", ""),
            "priority": data.get("priority", "medium"),
        }
    if any(not isinstance(value, str) for value in values.values()):
        return {}, "ticket fields must be strings"
    values = {field: value.strip() for field, value in values.items()}
    if "category" in values:
        values["category"] = values["category"].lower()
    if "priority" in values:
        values["priority"] = values["priority"].lower()
    if not partial and (
        not values["title"] or not values["description"] or not values["category"]
    ):
        return {}, "title, description and category are required"
    if "title" in values and not values["title"]:
        return {}, "title cannot be empty"
    if "description" in values and not values["description"]:
        return {}, "description cannot be empty"
    if "category" in values and not values["category"]:
        return {}, "category cannot be empty"
    if "title" in values and len(values["title"]) > 255:
        return {}, "title too long"
    if "category" in values and len(values["category"]) > 100:
        return {}, "category too long"
    if "category" in values and values["category"] not in ALLOWED_CATEGORIES:
        return {}, "invalid category"
    if "priority" in values and values["priority"] not in ALLOWED_PRIORITIES:
        return {}, "invalid priority"
    return values, None


@tickets_bp.post("")
@login_required
def create_ticket():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error="request body must be an object"), 400
    values, error = _ticket_data(data)
    if error:
        return jsonify(error=error), 400

    ticket = Ticket(
        **values,
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
    ticket = _get_owned_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    return jsonify(serialize_ticket(ticket))


@tickets_bp.patch("/<uuid:ticket_id>")
@login_required
def update_ticket(ticket_id: UUID):
    ticket = _get_owned_ticket(ticket_id, lock=True)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    if ticket.status != TicketStatus.NEW or ticket.technician_id is not None:
        return jsonify(error="Ticket cannot be changed in this status"), 409

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error="request body must be an object"), 400
    values, error = _ticket_data(data, partial=True)
    if error:
        return jsonify(error=error), 400
    for field, value in values.items():
        setattr(ticket, field, value)
    get_session().commit()
    get_session().refresh(ticket)
    return jsonify(serialize_ticket(ticket))


@tickets_bp.delete("/<uuid:ticket_id>")
@login_required
def delete_ticket(ticket_id: UUID):
    ticket = _get_owned_ticket(ticket_id, lock=True)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    if ticket.status != TicketStatus.NEW or ticket.technician_id is not None:
        return jsonify(error="Ticket cannot be deleted in this status"), 409

    session = get_session()
    session.delete(ticket)
    session.commit()
    return "", 204


@tickets_bp.post("/<uuid:ticket_id>/comments")
@login_required
def add_comment(ticket_id: UUID):
    ticket = _get_owned_ticket(ticket_id, lock=True)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    if ticket.status in {
        TicketStatus.RESOLVED,
        TicketStatus.CANCELLED,
        TicketStatus.ARCHIVED,
    }:
        return jsonify(error="Comments are disabled for this ticket"), 409

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error="request body must be an object"), 400
    content, error = validate_comment_content(data.get("content"))
    if error or content is None:
        return jsonify(error=error), 400

    comment = Comment(
        ticket_id=ticket.id,
        author_id=current_user_id(),
        content=content,
    )
    session = get_session()
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return jsonify(serialize_comment(comment)), 201


@tickets_bp.get("/<uuid:ticket_id>/comments")
@login_required
def list_comments(ticket_id: UUID):
    ticket = _get_owned_ticket(ticket_id)
    if ticket is None:
        return jsonify(error="Resource not found"), 404
    comments = get_session().scalars(
        select(Comment)
        .where(Comment.ticket_id == ticket.id)
        .order_by(Comment.created_at.asc())
    ).all()
    return jsonify([serialize_comment(comment) for comment in comments])