from enum import StrEnum


class UserRole(StrEnum):
    CLIENT = "client"
    TECHNICIAN = "technician"


class TicketStatus(StrEnum):
    NEW = "new"
    RESOLVED = "resolved"
    INSTATUS = "instatus"
    CANCELLED = "cancelled"
