"""Create the application schema with UUID identifiers."""

from alembic import op


revision = "20261111_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE TYPE user_role AS ENUM ('client', 'technician')")
    op.execute(
        "CREATE TYPE ticket_status AS ENUM "
        "('new', 'resolved', 'instatus', 'cancelled')"
    )
    op.execute(
        "CREATE TYPE ticket_category AS ENUM "
        "('hardware', 'software', 'network', 'access', 'other')"
    )
    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role user_role NOT NULL DEFAULT 'client',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT users_email_format_check
                CHECK (email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),
            CONSTRAINT users_password_hash_not_empty_check
                CHECK (length(btrim(password_hash)) > 0)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE tickets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            client_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            technician_id UUID REFERENCES users (id) ON DELETE SET NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category ticket_category NOT NULL,
            priority TEXT NOT NULL,
            status ticket_status NOT NULL DEFAULT 'new',
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT tickets_title_not_empty_check
                CHECK (length(btrim(title)) > 0),
            CONSTRAINT tickets_description_not_empty_check
                CHECK (length(btrim(description)) > 0),
            CONSTRAINT tickets_priority_not_empty_check
                CHECK (length(btrim(priority)) > 0)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE comments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticket_id UUID NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
            author_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    op.execute(
        """
        CREATE TABLE ticket_history (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticket_id UUID NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
            old_status ticket_status,
            new_status ticket_status NOT NULL,
            changed_by UUID NOT NULL REFERENCES users (id),
            changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    op.execute(
        """
        CREATE TABLE refresh_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS refresh_tokens, ticket_history, comments, tickets, users")
    op.execute("DROP TYPE ticket_category")
    op.execute("DROP TYPE ticket_status")
    op.execute("DROP TYPE user_role")
