import os
import unittest
from uuid import uuid4

from sqlalchemy import text

from app import create_app
from app.database import get_db


class AuthEndpointTestCase(unittest.TestCase):
    def setUp(self):
        database_url = os.getenv("TEST_DATABASE_URL")
        if not database_url:
            self.skipTest("Ustaw TEST_DATABASE_URL, aby uruchomić testy PostgreSQL")
        self.app = create_app(
            {"TESTING": True, "DATABASE_URL": database_url}
        )
        self.client = self.app.test_client()
        self.email = f"{uuid4()}@example.com"

    def tearDown(self):
        with self.app.app_context():
            get_db().execute(
                text("DELETE FROM users WHERE email = :email"),
                {"email": self.email},
            )
            get_db().commit()

    def test_register_login_refresh_and_logout(self):
        credentials = {"email": self.email, "password": "correct-password"}
        response = self.client.post("/api/auth/register", json=credentials)
        self.assertEqual(response.status_code, 201)
        tokens = response.get_json()
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)

        response = self.client.post("/api/auth/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        login_tokens = response.get_json()

        response = self.client.post(
            "/api/auth/refresh",
            json={"refresh_token": login_tokens["refresh_token"]},
        )
        self.assertEqual(response.status_code, 200)
        refreshed_tokens = response.get_json()

        response = self.client.post(
            "/api/auth/refresh",
            json={"refresh_token": login_tokens["refresh_token"]},
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.post(
            "/api/auth/logout",
            json={"refresh_token": refreshed_tokens["refresh_token"]},
        )
        self.assertEqual(response.status_code, 204)

    def test_register_and_login_validate_credentials(self):
        response = self.client.post(
            "/api/auth/register",
            json={"email": "invalid-email", "password": "correct-password"},
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/auth/register",
            json={"email": self.email, "password": "short"},
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/auth/login",
            json={"email": self.email, "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 401)
