from alembic import command
from alembic.config import Config
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from uuid import UUID

from app.auth.password import hash_password
from app.models import User, UserRole


def _sqlalchemy_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def get_db() -> Session:
    return get_session()


def get_session() -> Session:
    if "db_session" not in g:
        engine = create_engine(
            _sqlalchemy_url(current_app.config["DATABASE_URL"])
        )
        g.db_engine = engine
        g.db_session = sessionmaker(bind=engine, expire_on_commit=False)()
    return g.db_session


def close_db(_error: BaseException | None = None) -> None:
    session = g.pop("db_session", None)
    if session is not None:
        session.close()
    engine = g.pop("db_engine", None)
    if engine is not None:
        engine.dispose()


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


def create_user(email: str, password: str) -> UUID:
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=UserRole.CLIENT,
    )
    session = get_session()
    session.add(user)
    session.commit()
    return user.id


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    if app.config["INIT_DB"]:
        with app.app_context():
            init_db()
