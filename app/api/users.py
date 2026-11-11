from uuid import UUID

from flask import Blueprint, g, jsonify
from sqlalchemy import select

from app.auth.decorators import login_required
from app.database import get_session
from app.models import User


users_bp = Blueprint("users", __name__)


@users_bp.get("/me")
@login_required
def me():
    user = get_session().scalar(
        select(User).where(User.id == UUID(g.current_user["sub"]))
    )
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(id=str(user.id), email=user.email, role=user.role.value)