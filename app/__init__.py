import os

from flask import Flask, jsonify


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-me-in-development"),
    )

    @app.get("/")
    def index():
        return jsonify(
            name="DevSecOps service desk",
            status="ok",
        )

    return app


app = create_app()
