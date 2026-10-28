import os

from flask import Flask

from .api import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-development"),
    )
    app.register_blueprint(api_bp)

    return app


app = create_app()
