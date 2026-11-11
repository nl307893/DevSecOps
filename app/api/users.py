import re
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.auth.decorators import login_required
from app.auth.password import hash_password, verify_password
from app.database import get_session
from app.models import User
from .ticket_helpers import current_user_id, user_display_name


users_bp = Blueprint("users", __name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


@users_bp.get("/me")
@login_required
def me():
    user = _current_user()
    if user is None:
        return jsonify(error="User not found"), 404
    return _serialize_user(user)


@users_bp.patch("/me/name")
@login_required
def update_name():
    data = request.get_json(silent=True) or {}
    first_name = _required_name(data.get("first_name"))
    last_name = _required_name(data.get("last_name"))
    if first_name is None or last_name is None:
        return jsonify(error="first_name and last_name are required"), 400

    user = _current_user()
    if user is None:
        return jsonify(error="User not found"), 404
    user.first_name = first_name
    user.last_name = last_name
    get_session().commit()
    return _serialize_user(user)


@users_bp.patch("/me/email")
@login_required
def update_email():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not isinstance(email, str):
        return jsonify(error="email is required"), 400
    email = email.strip().lower()
    if len(email) > 255 or not EMAIL_PATTERN.fullmatch(email):
        return jsonify(error="invalid email"), 400

    user = _current_user()
    if user is None:
        return jsonify(error="User not found"), 404
    user.email = email
    try:
        get_session().commit()
    except IntegrityError:
        get_session().rollback()
        return jsonify(error="Email already registered"), 409
    return _serialize_user(user)


@users_bp.patch("/me/password")
@login_required
def update_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    if not isinstance(current_password, str) or not isinstance(
        new_password, str
    ):
        return jsonify(
            error="current_password and new_password are required"
        ), 400
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return jsonify(
            error=f"new password must be at least {MIN_PASSWORD_LENGTH} characters"
        ), 400

    user = _current_user()
    if user is None:
        return jsonify(error="User not found"), 404
    if not verify_password(current_password, user.password_hash):
        return jsonify(error="Invalid current password"), 400

    user.password_hash = hash_password(new_password)
    get_session().commit()
    return "", 204


@users_bp.delete("/me")
@login_required
def delete_account():
    data = request.get_json(silent=True) or {}
    password = data.get("password")
    if not isinstance(password, str):
        return jsonify(error="password is required"), 400

    user = _current_user()
    if user is None:
        return jsonify(error="User not found"), 404
    if not verify_password(password, user.password_hash):
        return jsonify(error="Invalid password"), 400

    session = get_session()
    session.delete(user)
    session.commit()
    return "", 204


@users_bp.get("/<uuid:user_id>")
@login_required
def get_user(user_id: UUID):
    if user_id != current_user_id() and g.current_user["role"] != "technician":
        return jsonify(error="Resource not found"), 404
    user = get_session().get(User, user_id)
    if user is None:
        return jsonify(error="Resource not found"), 404
    return _serialize_user(user)


def _current_user() -> User | None:
    return get_session().get(User, current_user_id())


def _required_name(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or len(value) > 100:
        return None
    return value


def _serialize_user(user: User):
    return jsonify(
        id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user_display_name(user),
        email=user.email,
        role=user.role.value,
    )