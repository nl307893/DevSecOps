from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from flask import current_app
from sqlalchemy import select

from app.database import get_session
from app.models import RefreshToken, User
from .password import hash_password, verify_password


def create_access_token(user_id: UUID, role: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=current_app.config["JWT_ACCESS_MINUTES"]
    )
    return jwt.encode(
        {"sub": str(user_id), "role": role, "type": "access",
         "iat": now, "exp": expires_at},
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(user_id: UUID) -> str:
    token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=current_app.config["JWT_REFRESH_DAYS"]
    )
    session = get_session()
    session.add(
        RefreshToken(
            user_id=user_id,
            token_hash=_hash_refresh_token(token),
            expires_at=expires_at,
        )
    )
    session.commit()
    return token


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"],
    )
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")
    return payload


def rotate_refresh_token(token: str) -> tuple[dict, str]:
    token_hash = _hash_refresh_token(token)
    session = get_session()
    refresh_token = session.scalar(
        select(RefreshToken)
        .join(RefreshToken.user)
        .where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(timezone.utc),
        )
    )
    if refresh_token is None:
        raise ValueError("Invalid refresh token")

    refresh_token.revoked_at = datetime.now(timezone.utc)
    new_token = create_refresh_token(refresh_token.user_id)
    session.commit()
    return refresh_token.user, new_token


def revoke_refresh_token(token: str) -> None:
    session = get_session()
    refresh_token = session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == _hash_refresh_token(token),
            RefreshToken.revoked_at.is_(None),
        )
    )
    if refresh_token is not None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        session.commit()
