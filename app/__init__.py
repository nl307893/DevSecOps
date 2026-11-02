import os

from flask import Flask

from .api import api_bp
from .database import init_app


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-development"),
        DATABASE=os.path.join(app.instance_path, "app.sqlite3"),
    )
    if test_config is not None:
        app.config.update(test_config)

    init_app(app)
    app.register_blueprint(api_bp)

    return app


app = create_app()
