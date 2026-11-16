import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from app import create_app
from app.api.Client.tickets import _ticket_data
from app.api.Client.users import _required_name
from app.api.ticket_helpers import validate_comment_content
from app.auth.decorators import login_required
from app.auth.password import hash_password, verify_password
from app.auth.service import create_refresh_token, revoke_refresh_token


class PasswordUnitTestCase(unittest.TestCase):
    def test_hash_password_can_be_verified(self):
        password_hash = hash_password("correct-password")

        self.assertTrue(verify_password("correct-password", password_hash))

    def test_verify_password_rejects_wrong_password(self):
        password_hash = hash_password("correct-password")

        self.assertFalse(verify_password("wrong-password", password_hash))


class CommentValidationUnitTestCase(unittest.TestCase):
    def test_validate_comment_content_strips_surrounding_whitespace(self):
        self.assertEqual(
            validate_comment_content("  Problem nadal wystepuje  "),
            ("Problem nadal wystepuje", None),
        )

    def test_validate_comment_content_rejects_non_string(self):
        self.assertEqual(
            validate_comment_content(None),
            (None, "content is required"),
        )

    def test_validate_comment_content_rejects_empty_content(self):
        self.assertEqual(
            validate_comment_content("   "),
            (None, "content cannot be empty"),
        )

    def test_validate_comment_content_rejects_content_over_limit(self):
        self.assertEqual(
            validate_comment_content("a" * 5001),
            (None, "content too long"),
        )


class TicketValidationUnitTestCase(unittest.TestCase):
    def test_ticket_data_normalizes_valid_values(self):
        values, error = _ticket_data(
            {
                "title": "  Awaria drukarki ",
                "description": "  Nie drukuje ",
                "category": " HARDWARE ",
                "priority": " HIGH ",
            }
        )

        self.assertIsNone(error)
        self.assertEqual(
            values,
            {
                "title": "Awaria drukarki",
                "description": "Nie drukuje",
                "category": "hardware",
                "priority": "high",
            },
        )

    def test_ticket_data_requires_title_description_and_category(self):
        values, error = _ticket_data({"title": "Title"})

        self.assertEqual(values, {})
        self.assertEqual(error, "title, description and category are required")

    def test_ticket_data_rejects_invalid_priority(self):
        values, error = _ticket_data(
            {
                "title": "Title",
                "description": "Description",
                "category": "hardware",
                "priority": "urgent",
            }
        )

        self.assertEqual(values, {})
        self.assertEqual(error, "invalid priority")

    def test_ticket_data_partial_update_requires_a_field(self):
        values, error = _ticket_data({}, partial=True)

        self.assertEqual(values, {})
        self.assertEqual(error, "at least one ticket field is required")


class UserValidationUnitTestCase(unittest.TestCase):
    def test_required_name_strips_valid_name(self):
        self.assertEqual(_required_name("  Jan  "), "Jan")

    def test_required_name_rejects_empty_name(self):
        self.assertIsNone(_required_name("   "))


class MockedDependencyUnitTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "INIT_DB": False,
                "DATABASE_URL": "postgresql://unused",
            }
        )

    def test_create_refresh_token_uses_session_and_persists_token(self):
        user_id = uuid4()

        with (
            self.app.app_context(),
            patch("app.auth.service.get_session") as get_session,
            patch(
                "app.auth.service.secrets.token_urlsafe",
                return_value="refresh-token",
            ),
        ):
            token = create_refresh_token(user_id)

        session = get_session.return_value
        refresh_token = session.add.call_args.args[0]
        self.assertEqual(token, "refresh-token")
        self.assertEqual(refresh_token.user_id, user_id)
        self.assertIsNotNone(refresh_token.expires_at)
        session.commit.assert_called_once_with()

    def test_revoke_refresh_token_updates_mocked_record(self):
        refresh_token = Mock(revoked_at=None)
        session = Mock()
        session.scalar.return_value = refresh_token

        with patch("app.auth.service.get_session", return_value=session):
            revoke_refresh_token("refresh-token")

        self.assertIsNotNone(refresh_token.revoked_at)
        session.commit.assert_called_once_with()

    def test_login_required_uses_mocked_token_decoder(self):
        app = self.app

        @login_required
        def protected_view():
            return "protected"

        with (
            app.test_request_context(
                "/protected",
                headers={"Authorization": "Bearer access-token"},
            ),
            patch(
                "app.auth.decorators.decode_access_token",
                return_value={"sub": str(uuid4()), "role": "client"},
            ) as decode_access_token,
        ):
            response = protected_view()

        self.assertEqual(response, "protected")
        decode_access_token.assert_called_once_with("access-token")

