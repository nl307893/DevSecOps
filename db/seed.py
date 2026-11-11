import os
import re

from sqlalchemy import select

from app import create_app
from app.auth.password import hash_password
from app.database import get_session
from app.models import User, UserRole


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def seed_demo_users(
    client_email: str,
    client_password: str,
    technician_email: str,
    technician_password: str,
) -> None:
    session = get_session()
    users = (
        (client_email, client_password, "Demo", "Client", UserRole.CLIENT),
        (
            technician_email,
            technician_password,
            "Demo",
            "Technician",
            UserRole.TECHNICIAN,
        ),
    )
    for email, password, first_name, last_name, role in users:
        user = session.scalar(select(User).where(User.email == email))
        if user is None:
            session.add(
                User(
                    email=email,
                    password_hash=hash_password(password),
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                )
            )
    session.commit()


def main() -> None:
    if os.getenv("SEED_DEMO_DATA") != "1":
        raise RuntimeError(
            "Set SEED_DEMO_DATA=1 to explicitly enable demo seeding"
        )

    values = {
        "client_email": os.getenv("SEED_CLIENT_EMAIL"),
        "client_password": os.getenv("SEED_CLIENT_PASSWORD"),
        "technician_email": os.getenv("SEED_TECHNICIAN_EMAIL"),
        "technician_password": os.getenv("SEED_TECHNICIAN_PASSWORD"),
    }
    if any(value is None for value in values.values()):
        raise RuntimeError(
            "Set all SEED_CLIENT_* and SEED_TECHNICIAN_* variables"
        )
    if not all(EMAIL_PATTERN.fullmatch(values[key]) for key in (
        "client_email",
        "technician_email",
    )):
        raise RuntimeError("Seed email variables must contain valid emails")

    app = create_app()
    with app.app_context():
        seed_demo_users(**values)
    print("Demo client and technician users are ready.")


if __name__ == "__main__":
    main()
