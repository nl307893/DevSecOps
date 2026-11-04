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


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify(error="email and password are required"), 400

    user = User(
        email=email,
        password_hash=hash_password(password),
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
