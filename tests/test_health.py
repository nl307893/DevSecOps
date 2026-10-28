import unittest

from app import create_app


class HealthEndpointTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health_returns_application_status_without_login(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})
        self.assertEqual(response.content_type, "application/json")
