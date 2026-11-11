from flask import Blueprint

from .health import health_bp
from .auth import auth_bp
from .Client import tickets_bp, users_bp
from .technician_tickets import technician_tickets_bp


api_bp = Blueprint("api", __name__)
api_bp.register_blueprint(health_bp, url_prefix="/api")
api_bp.register_blueprint(auth_bp, url_prefix="/api/auth")
api_bp.register_blueprint(tickets_bp, url_prefix="/api/tickets")
api_bp.register_blueprint(
    technician_tickets_bp, url_prefix="/api/technician/tickets"
)
api_bp.register_blueprint(users_bp, url_prefix="/api/users")