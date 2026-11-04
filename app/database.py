from typing import Any

from alembic import command
from alembic.config import Config
from flask import current_app, g
import psycopg
from psycopg.rows import dict_row
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash


def _sqlalchemy_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def get_db() -> psycopg.Connection[dict[str, Any]]:
    if "db" not in g:
        g.db = psycopg.connect(
            current_app.config["DATABASE_URL"],
            row_factory=dict_row,
        )
    return g.db


def close_db(_error: BaseException | None = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    alembic_config = Config(str(current_app.config["ALEMBIC_CONFIG"]))
    engine = create_engine(
        _sqlalchemy_url(current_app.config["DATABASE_URL"])
    )

    try:
        with engine.begin() as connection:
            alembic_config.attributes["connection"] = connection
            command.upgrade(alembic_config, "head")
    finally:
        engine.dispose()


def create_user(email: str, password: str) -> int:
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
        (email, generate_password_hash(password)),
    )
    db.commit()
    return cursor.fetchone()["id"]


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    if app.config["INIT_DB"]:
        with app.app_context():
            init_db()
