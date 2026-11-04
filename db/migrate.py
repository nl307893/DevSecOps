import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine

from app.database import _sqlalchemy_url


ROOT_DIR = Path(__file__).resolve().parent.parent


def main() -> None:
    load_dotenv(ROOT_DIR / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set in .env")

    config = Config(str(ROOT_DIR / "alembic.ini"))
    engine = create_engine(_sqlalchemy_url(database_url))
    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
