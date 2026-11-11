import re

from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.auth.service import (
    create_access_token,
    create_refresh_token,
    hash_password,
    revoke_refresh_token,
    rotate_refresh_token,
    verify_password,
)
from app.database import get_session
from app.models import User, UserRole


auth_bp = Blueprint("auth", __name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 12


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error="request body must be an object"), 400
    email = data.get("email")
    password = data.get("password", "")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    first_name = first_name.strip() if isinstance(first_name, str) else None
    last_name = last_name.strip() if isinstance(last_name, str) else None
    if not isinstance(email, str) or not EMAIL_PATTERN.fullmatch(email.strip()):
        return jsonify(error="invalid email"), 400
    email = email.strip().lower()
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        return jsonify(
            error=f"password must be at least {MIN_PASSWORD_LENGTH} characters"
        ), 400
    if (first_name and len(first_name) > 100) or (
        last_name and len(last_name) > 100
    ):
        return jsonify(error="first name or last name too long"), 400

    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=UserRole.CLIENT,
    )
    session = get_session()
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return jsonify(error="Email already registered"), 409

    return _tokens(user), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = get_session().scalar(
        select(User).where(
            User.email == data.get("email", "").strip().lower()
        )
    )
    if user is None or not verify_password(
        data.get("password", ""), user.password_hash
    ):
        return jsonify(error="Invalid credentials"), 401
    return _tokens(user)


@auth_bp.post("/refresh")
def refresh():
    token = (request.get_json(silent=True) or {}).get("refresh_token", "")
    try:
        row, new_refresh_token = rotate_refresh_token(token)
    except ValueError:
        return jsonify(error="Invalid refresh token"), 401
    return jsonify(
        access_token=create_access_token(row.id, row.role.value),
        refresh_token=new_refresh_token,
        token_type="Bearer",
    )


@auth_bp.post("/logout")
def logout():
    token = (request.get_json(silent=True) or {}).get("refresh_token", "")
    revoke_refresh_token(token)
    return "", 204


def _tokens(user: User) -> tuple:
    return jsonify(
        access_token=create_access_token(user.id, user.role.value),
        refresh_token=create_refresh_token(user.id),
        token_type="Bearer",
    )
