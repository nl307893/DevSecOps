from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, Enum, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import UserRole

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .ticket import Ticket


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            r"email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'",
            name="users_email_format_check",
        ),
        CheckConstraint(
            "length(btrim(password_hash)) > 0",
            name="users_password_hash_not_empty_check",
        ),
        CheckConstraint(
            "first_name IS NULL OR length(btrim(first_name)) > 0",
            name="users_first_name_not_empty_check",
        ),
        CheckConstraint(
            "last_name IS NULL OR length(btrim(last_name)) > 0",
            name="users_last_name_not_empty_check",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=UserRole.CLIENT,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )

    client_tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="client", foreign_keys="Ticket.client_id"
    )
    technician_tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="technician", foreign_keys="Ticket.technician_id"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
