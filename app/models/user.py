from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum, String, func
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
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
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
