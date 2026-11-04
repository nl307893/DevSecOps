import os
import unittest

import bcrypt
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.database import create_user, get_db
from app.models import Ticket, User


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        database_url = os.getenv("TEST_DATABASE_URL")
        if not database_url:
            self.skipTest("Ustaw TEST_DATABASE_URL, aby uruchomić testy PostgreSQL")
        self.app = create_app(
            {"TESTING": True, "DATABASE_URL": database_url}
        )

    def tearDown(self):
        with self.app.app_context():
            get_db().execute(text(
                "DROP TABLE IF EXISTS "
                "refresh_tokens, ticket_history, comments, tickets, users, "
                "alembic_version CASCADE"
            ))
            get_db().execute(text(
                "DROP TYPE IF EXISTS ticket_status, user_role CASCADE"
            ))
            get_db().commit()

    def test_database_is_created_with_related_tables(self):
        with self.app.app_context():
            db = get_db()
            tables = {
                row["table_name"]
                for row in db.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' "
                    "AND table_name IN ('users', 'tickets')"
                )).mappings()
            }
            foreign_keys = db.execute(text(
                "SELECT kcu.column_name AS column_name, "
                "ccu.table_name AS foreign_table_name "
                "FROM information_schema.table_constraints AS tc "
                "JOIN information_schema.key_column_usage AS kcu "
                "ON tc.constraint_name = kcu.constraint_name "
                "JOIN information_schema.constraint_column_usage AS ccu "
                "ON ccu.constraint_name = tc.constraint_name "
                "WHERE tc.constraint_type = 'FOREIGN KEY' "
                "AND tc.table_name = 'tickets'"
            )).mappings().all()

        self.assertEqual(tables, {"users", "tickets"})
        self.assertTrue(foreign_keys, "Tabela tickets powinna mieć klucz obcy")
        self.assertEqual(foreign_keys[0]["foreign_table_name"], "users")
        self.assertEqual(foreign_keys[0]["column_name"], "client_id")

    def test_user_password_is_stored_as_a_hash(self):
        with self.app.app_context():
            user_id = create_user("user@example.com", "correct-password")
            row = get_db().get(User, user_id)

        self.assertIsNotNone(row)
        self.assertNotEqual(row.password_hash, "correct-password")
        self.assertTrue(
            bcrypt.checkpw(
                b"correct-password", row.password_hash.encode()
            )
        )

    def test_ticket_requires_existing_user(self):
        with self.app.app_context():
            db = get_db()
            with self.assertRaises(IntegrityError):
                db.add(
                    Ticket(
                        client_id=999,
                        title="Title",
                        description="Description",
                        category="Hardware",
                        priority="high",
                    )
                )
                db.flush()
