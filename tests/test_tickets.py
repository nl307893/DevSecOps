import os
import unittest
from uuid import uuid4

from sqlalchemy import text

from app import create_app
from app.database import get_db


class TicketEndpointTestCase(unittest.TestCase):
    def setUp(self):
        database_url = os.getenv("TEST_DATABASE_URL")
        if not database_url:
            self.skipTest("Ustaw TEST_DATABASE_URL, aby uruchomić testy PostgreSQL")
        self.app = create_app({"TESTING": True, "DATABASE_URL": database_url})
        self.client = self.app.test_client()
        self.emails = []

    def tearDown(self):
        with self.app.app_context():
            for email in self.emails:
                get_db().execute(
                    text("DELETE FROM users WHERE email = :email"),
                    {"email": email},
                )
            get_db().commit()

    def _register(self):
        email = f"{uuid4()}@example.com"
        self.emails.append(email)
        response = self.client.post(
            "/api/auth/register",
            json={"email": email, "password": "correct-password"},
        )
        self.assertEqual(response.status_code, 201)
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def _payload(self, **overrides):
        payload = {
            "title": "Awaria drukarki",
            "description": "Drukarka nie drukuje",
            "category": "hardware",
            "priority": "high",
        }
        payload.update(overrides)
        return payload

    def test_requires_authentication(self):
        self.assertEqual(self.client.get("/api/tickets").status_code, 401)
        self.assertEqual(
            self.client.post("/api/tickets", json=self._payload()).status_code, 401
        )

    def test_create_and_get_ticket(self):
        headers = self._register()
        response = self.client.post(
            "/api/tickets", json=self._payload(), headers=headers
        )
        self.assertEqual(response.status_code, 201)
        ticket = response.get_json()
        self.assertEqual(ticket["status"], "new")  # popraw, jeśli enum ma inną wartość

        response = self.client.get(f"/api/tickets/{ticket['id']}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["title"], "Awaria drukarki")

    def test_validation_errors(self):
        headers = self._register()
        response = self.client.post(
            "/api/tickets", json=self._payload(title=""), headers=headers
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            "/api/tickets", json=self._payload(priority="urgent!"), headers=headers
        )
        self.assertEqual(response.status_code, 400)

    def test_client_sees_only_own_tickets(self):
        headers_a = self._register()
        headers_b = self._register()
        response = self.client.post(
            "/api/tickets", json=self._payload(), headers=headers_a
        )
        ticket_id = response.get_json()["id"]

        listed = self.client.get("/api/tickets", headers=headers_b).get_json()
        self.assertEqual(listed, [])

        response = self.client.get(f"/api/tickets/{ticket_id}", headers=headers_b)
        self.assertEqual(response.status_code, 404)

    def test_client_cannot_update_another_users_ticket(self):
        owner_headers = self._register()
        attacker_headers = self._register()
        create_response = self.client.post(
            "/api/tickets",
            json=self._payload(),
            headers=owner_headers,
        )
        ticket_id = create_response.get_json()["id"]

        update_response = self.client.patch(
            f"/api/tickets/{ticket_id}",
            json={"title": "Nieautoryzowana zmiana"},
            headers=attacker_headers,
        )

        self.assertEqual(update_response.status_code, 404)

    def test_client_cannot_delete_another_users_ticket(self):
        owner_headers = self._register()
        attacker_headers = self._register()
        create_response = self.client.post(
            "/api/tickets",
            json=self._payload(),
            headers=owner_headers,
        )
        ticket_id = create_response.get_json()["id"]

        delete_response = self.client.delete(
            f"/api/tickets/{ticket_id}",
            headers=attacker_headers,
        )

        self.assertEqual(delete_response.status_code, 404)

    def test_client_cannot_comment_on_another_users_ticket(self):
        owner_headers = self._register()
        attacker_headers = self._register()
        create_response = self.client.post(
            "/api/tickets",
            json=self._payload(),
            headers=owner_headers,
        )
        ticket_id = create_response.get_json()["id"]

        comment_response = self.client.post(
            f"/api/tickets/{ticket_id}/comments",
            json={"content": "Nieautoryzowany komentarz"},
            headers=attacker_headers,
        )

        self.assertEqual(comment_response.status_code, 404)

    def test_client_cannot_access_technician_endpoints(self):
        client_headers = self._register()

        list_response = self.client.get(
            "/api/technician/tickets",
            headers=client_headers,
        )
        assigned_response = self.client.get(
            "/api/technician/tickets/assigned",
            headers=client_headers,
        )

        self.assertEqual(list_response.status_code, 404)
        self.assertEqual(assigned_response.status_code, 404)

    def test_ticket_not_found(self):
        headers = self._register()
        response = self.client.get("/api/tickets/999999999", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_client_can_update_comment_and_delete_new_ticket(self):
        headers = self._register()
        response = self.client.post(
            "/api/tickets", json=self._payload(), headers=headers
        )
        self.assertEqual(response.status_code, 201)
        ticket_id = response.get_json()["id"]

        response = self.client.patch(
            f"/api/tickets/{ticket_id}",
            json={"title": "Zmieniony tytul"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["title"], "Zmieniony tytul")

        response = self.client.post(
            f"/api/tickets/{ticket_id}/comments",
            json={"content": "Komentarz klienta"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.get(
            f"/api/tickets/{ticket_id}/comments", headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["content"], "Komentarz klienta")

        response = self.client.delete(
            f"/api/tickets/{ticket_id}", headers=headers
        )
        self.assertEqual(response.status_code, 204)