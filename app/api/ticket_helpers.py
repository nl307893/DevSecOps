from uuid import UUID

from flask import g

from app.models import Comment, Ticket


def current_user_id() -> UUID:
    return UUID(g.current_user["sub"])


def user_display_name(user) -> str:
    name = " ".join(
        part for part in (user.first_name, user.last_name) if part
    )
    return name or user.email


def serialize_ticket(ticket: Ticket, include_priority: bool = False) -> dict:
    serialized = {
        "id": str(ticket.id),
        "title": ticket.title,
        "description": ticket.description,
        "category": ticket.category.value,
        "status": ticket.status.value,
        "client_name": user_display_name(ticket.client),
        "technician_name": (
            user_display_name(ticket.technician)
            if ticket.technician
            else None
        ),
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
    }
    if include_priority:
        serialized["priority"] = ticket.priority
    return serialized


def serialize_comment(comment: Comment) -> dict:
    return {
        "id": str(comment.id),
        "content": comment.content,
        "author_name": user_display_name(comment.author),
        "created_at": (
            comment.created_at.isoformat() if comment.created_at else None
        ),
    }


def validate_comment_content(content: object) -> tuple[str | None, str | None]:
    if not isinstance(content, str):
        return None, "content is required"
    content = content.strip()
    if not content:
        return None, "content cannot be empty"
    if len(content) > 5000:
        return None, "content too long"
    return content, None
