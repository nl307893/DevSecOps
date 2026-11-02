import sqlite3
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.database import create_user, get_db
from werkzeug.security import check_password_hash


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.sqlite3"
        self.app = create_app(
            {"TESTING": True, "DATABASE": str(database_path)}
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_is_created_with_related_tables(self):
        with self.app.app_context():
            db = get_db()
            tables = {
                row["name"]
                for row in db.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name IN ('users', 'tickets')"
                )
            }
            foreign_keys = db.execute(
                "PRAGMA foreign_key_list(tickets)"
            ).fetchall()

        self.assertEqual(tables, {"users", "tickets"})
        self.assertTrue(foreign_keys, "Tabela tickets powinna mieć klucz obcy")
        self.assertEqual(foreign_keys[0]["table"], "users")
        self.assertEqual(foreign_keys[0]["from"], "user_id")

    def test_user_password_is_stored_as_a_hash(self):
        with self.app.app_context():
            user_id = create_user("user@example.com", "correct-password")
            row = get_db().execute(
                "SELECT password_hash FROM users WHERE id = ?", (user_id,)
            ).fetchone()

        self.assertIsNotNone(row)
        self.assertNotEqual(row["password_hash"], "correct-password")
        self.assertTrue(
            check_password_hash(row["password_hash"], "correct-password")
        )

    def test_ticket_requires_existing_user(self):
        with self.app.app_context():
            db = get_db()
            foreign_keys_enabled = db.execute(
                "PRAGMA foreign_keys"
            ).fetchone()[0]
            self.assertEqual(foreign_keys_enabled, 1)

            with self.assertRaises(sqlite3.IntegrityError):
                db.execute(
                    "INSERT INTO tickets "
                    "(user_id, title, description, category, priority) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (999, "Title", "Description", "Hardware", "high"),
                )