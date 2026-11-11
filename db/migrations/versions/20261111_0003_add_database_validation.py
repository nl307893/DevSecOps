"""Add ticket categories and database validation constraints."""

from alembic import op


revision = "20261111_0003"
down_revision = "20261104_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE ticket_category AS ENUM "
        "('hardware', 'software', 'network', 'access', 'other')"
    )
    op.execute(
        """
        ALTER TABLE tickets
        ALTER COLUMN category DROP DEFAULT,
        ALTER COLUMN category TYPE ticket_category
        USING (
            CASE lower(category)
                WHEN 'hardware' THEN 'hardware'
                WHEN 'software' THEN 'software'
                WHEN 'network' THEN 'network'
                WHEN 'access' THEN 'access'
                ELSE 'other'
            END
        )::ticket_category
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ADD CONSTRAINT users_email_format_check
        CHECK (email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$')
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ADD CONSTRAINT users_password_hash_not_empty_check
        CHECK (length(btrim(password_hash)) > 0)
        """
    )
    op.execute(
        """
        ALTER TABLE tickets
        ADD CONSTRAINT tickets_title_not_empty_check
        CHECK (length(btrim(title)) > 0),
        ADD CONSTRAINT tickets_description_not_empty_check
        CHECK (length(btrim(description)) > 0),
        ADD CONSTRAINT tickets_priority_not_empty_check
        CHECK (length(btrim(priority)) > 0)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE tickets
        DROP CONSTRAINT tickets_title_not_empty_check,
        DROP CONSTRAINT tickets_description_not_empty_check,
        DROP CONSTRAINT tickets_priority_not_empty_check
        """
    )
    op.execute(
        "ALTER TABLE users "
        "DROP CONSTRAINT users_email_format_check, "
        "DROP CONSTRAINT users_password_hash_not_empty_check"
    )
    op.execute(
        "ALTER TABLE tickets ALTER COLUMN category TYPE TEXT "
        "USING category::text"
    )
    op.execute("DROP TYPE ticket_category")
