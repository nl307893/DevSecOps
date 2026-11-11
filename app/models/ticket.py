from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import TicketCategory, TicketStatus

if TYPE_CHECKING:
    from .comment import Comment
    from .user import User


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "length(btrim(title)) > 0",
            name="tickets_title_not_empty_check",
        ),
        CheckConstraint(
            "length(btrim(description)) > 0",
            name="tickets_description_not_empty_check",
        ),
        CheckConstraint(
            "length(btrim(priority)) > 0",
            name="tickets_priority_not_empty_check",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[TicketCategory] = mapped_column(
        Enum(
            TicketCategory,
            name="ticket_category",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(
            TicketStatus,
            name="ticket_status",
            native_enum=True,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=TicketStatus.NEW,
    )
    client_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.current_timestamp()
    )

    client: Mapped["User"] = relationship(
        back_populates="client_tickets", foreign_keys=[client_id]
    )
    technician: Mapped["User | None"] = relationship(
        back_populates="technician_tickets", foreign_keys=[technician_id]
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
