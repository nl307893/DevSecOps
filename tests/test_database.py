import os
import unittest

from psycopg import IntegrityError
from werkzeug.security import check_password_hash

from app import create_app
from app.database import create_user, get_db


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
            get_db().execute(
                "DROP TABLE IF EXISTS tickets, users, alembic_version CASCADE"
            )
            get_db().commit()

    def test_database_is_created_with_related_tables(self):
        with self.app.app_context():
            db = get_db()
            tables = {
                row["table_name"]
                for row in db.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' "
                    "AND table_name IN ('users', 'tickets')"
                )
            }
            foreign_keys = db.execute(
                "SELECT kcu.column_name AS column_name, "
                "ccu.table_name AS foreign_table_name "
                "FROM information_schema.table_constraints AS tc "
                "JOIN information_schema.key_column_usage AS kcu "
                "ON tc.constraint_name = kcu.constraint_name "
                "JOIN information_schema.constraint_column_usage AS ccu "
                "ON ccu.constraint_name = tc.constraint_name "
                "WHERE tc.constraint_type = 'FOREIGN KEY' "
                "AND tc.table_name = 'tickets'"
            ).fetchall()

        self.assertEqual(tables, {"users", "tickets"})
        self.assertTrue(foreign_keys, "Tabela tickets powinna mieć klucz obcy")
        self.assertEqual(foreign_keys[0]["foreign_table_name"], "users")
        self.assertEqual(foreign_keys[0]["column_name"], "user_id")

    def test_user_password_is_stored_as_a_hash(self):
        with self.app.app_context():
            user_id = create_user("user@example.com", "correct-password")
            row = get_db().execute(
                "SELECT password_hash FROM users WHERE id = %s", (user_id,)
            ).fetchone()

        self.assertIsNotNone(row)
        self.assertNotEqual(row["password_hash"], "correct-password")
        self.assertTrue(
            check_password_hash(row["password_hash"], "correct-password")
        )

    def test_ticket_requires_existing_user(self):
        with self.app.app_context():
            db = get_db()
            with self.assertRaises(IntegrityError):
                db.execute(
                    "INSERT INTO tickets "
                    "(user_id, title, description, category, priority) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (999, "Title", "Description", "Hardware", "high"),
                )
