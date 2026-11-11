from enum import StrEnum


class UserRole(StrEnum):
    CLIENT = "client"
    TECHNICIAN = "technician"


class TicketStatus(StrEnum):
    NEW = "new"
    RESOLVED = "resolved"
    INSTATUS = "instatus"
    CANCELLED = "cancelled"


class TicketCategory(StrEnum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    ACCESS = "access"
    OTHER = "other"
