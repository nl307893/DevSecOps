import pytest
from flask import Flask
from sqlalchemy import text

from app.database import get_session


@pytest.mark.integration
def test_database_is_created_with_related_tables(db_app: Flask) -> None:
    with db_app.app_context():
        db = get_session()
        tables = {
            row["table_name"]
            for row in db.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' "
                    "AND table_name IN ('users', 'tickets')"
                )
            ).mappings()
        }
        foreign_keys = db.execute(
            text(
                "SELECT kcu.column_name AS column_name, "
                "ccu.table_name AS foreign_table_name "
                "FROM information_schema.table_constraints AS tc "
                "JOIN information_schema.key_column_usage AS kcu "
                "ON tc.constraint_name = kcu.constraint_name "
                "JOIN information_schema.constraint_column_usage AS ccu "
                "ON ccu.constraint_name = tc.constraint_name "
                "WHERE tc.constraint_type = 'FOREIGN KEY' "
                "AND tc.table_name = 'tickets'"
            )
        ).mappings().all()

    assert tables == {"users", "tickets"}
    assert foreign_keys
    assert foreign_keys[0]["foreign_table_name"] == "users"
    assert foreign_keys[0]["column_name"] == "client_id"
