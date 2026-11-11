import os
import unittest
from uuid import uuid4

from sqlalchemy import select, text

from app import create_app
from app.database import get_db
from app.models import User, UserRole
from db.seed import seed_demo_users


class SeedTestCase(unittest.TestCase):
    def setUp(self):
        database_url = os.getenv("TEST_DATABASE_URL")
        if not database_url:
            self.skipTest("Ustaw TEST_DATABASE_URL, aby uruchomić testy PostgreSQL")
        self.app = create_app(
            {"TESTING": True, "DATABASE_URL": database_url}
        )
        suffix = uuid4()
        self.client_email = f"seed-client-{suffix}@example.com"
        self.technician_email = f"seed-technician-{suffix}@example.com"

    def tearDown(self):
        with self.app.app_context():
            get_db().execute(
                text("DELETE FROM users WHERE email IN (:client, :technician)"),
                {
                    "client": self.client_email,
                    "technician": self.technician_email,
                },
            )
            get_db().commit()

    def test_seed_creates_client_and_technician_idempotently(self):
        with self.app.app_context():
            seed_demo_users(
                self.client_email,
                "client-password",
                self.technician_email,
                "technician-password",
            )
            seed_demo_users(
                self.client_email,
                "client-password",
                self.technician_email,
                "technician-password",
            )
            users = get_db().scalars(
                select(User).where(
                    User.email.in_(
                        [self.client_email, self.technician_email]
                    )
                )
            ).all()

        self.assertEqual(len(users), 2)
        self.assertEqual(
            {user.role for user in users},
            {UserRole.CLIENT, UserRole.TECHNICIAN},
        )
