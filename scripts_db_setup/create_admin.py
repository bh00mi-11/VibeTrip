import os
import sys
import argparse
from datetime import datetime
from backend.database import SessionLocal, engine
from backend.models import Base, User
from backend.auth import hash_password

def create_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    admin_email = os.getenv("ADMIN_EMAIL", "admin@vibetrip.internal")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        parser = argparse.ArgumentParser(description="Create initial VibeTrip admin user.")
        parser.add_argument("--email", default=admin_email, help="Admin email address")
        parser.add_argument("--password", required=False, help="Admin password (min 8 characters)")
        parser.add_argument("--name", default="System Administrator", help="Admin display name")
        args, _ = parser.parse_known_args()

        admin_email = args.email
        admin_password = args.password
        admin_name = args.name

    if not admin_password:
        # Prompt securely or error if non-interactive
        import getpass
        try:
            admin_password = getpass.getpass("Enter Admin Password (min 8 characters): ")
        except Exception:
            pass

    if not admin_password or len(admin_password) < 8:
        print("Error: Admin password must be provided via ADMIN_PASSWORD env var, --password flag, or interactive prompt (min 8 chars).")
        sys.exit(1)

    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        existing.password_hash = hash_password(admin_password)
        existing.role = "admin"
        existing.is_active = True
        db.commit()
        print(f"Updated existing admin user: {admin_email}")
    else:
        new_admin = User(
            name=admin_name if 'admin_name' in locals() else "System Administrator",
            email=admin_email,
            password_hash=hash_password(admin_password),
            role="admin",
            is_active=True,
            is_demo=False,
            created_at=datetime.utcnow()
        )
        db.add(new_admin)
        db.commit()
        print(f"Successfully created initial Admin account: {admin_email}")

    db.close()

if __name__ == "__main__":
    create_admin()
