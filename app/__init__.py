import os
from pathlib import Path

from flask import Flask
from dotenv import load_dotenv

from .api import api_bp
from .database import init_app


load_dotenv()


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-development"),
        INIT_DB=True,
        DATABASE_URL=os.getenv("DATABASE_URL"),
        ALEMBIC_CONFIG=str(Path(__file__).resolve().parent.parent / "alembic.ini"),
    )
    if test_config is not None:
        app.config.update(test_config)

    init_app(app)
    app.register_blueprint(api_bp)

    return app
