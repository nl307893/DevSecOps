from functools import wraps
from typing import Callable

import jwt
from flask import g, jsonify, request

from .service import decode_access_token


def login_required(view: Callable) -> Callable:
    @wraps(view)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return jsonify(error="Authentication required"), 401
        try:
            g.current_user = decode_access_token(token)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify(error="Invalid or expired token"), 401
        return view(*args, **kwargs)

    return wrapped


def roles_required(*roles: str) -> Callable:
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.current_user["role"] not in roles:
                return jsonify(error="Resource not found"), 404
            return view(*args, **kwargs)

        return wrapped

    return decorator
