#!/usr/bin/env python3
"""
Create Admin User for AR Control Hub

This script creates an administrative user for the AR Control Hub system.
Use this during production deployment to create the initial admin account.

Usage:
    python scripts/create_admin_user.py \
        --email admin@company.com \
        --username admin \
        --password 'SecurePassword123!' \
        --full-name "System Administrator"
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from src.models import User
from src.db.base import Base


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user(
    email: str,
    username: str,
    password: str,
    full_name: str,
    database_url: str
):
    """Create an admin user in the database."""

    # Create async engine
    engine = create_async_engine(database_url, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with async_session() as session:
            # Check if user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"❌ User with email '{email}' already exists!")
                print(f"   User ID: {existing_user.id}")
                print(f"   Username: {existing_user.username}")
                print(f"   Role: {existing_user.role}")
                return False

            # Create new admin user
            hashed_password = pwd_context.hash(password)

            admin_user = User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                full_name=full_name,
                role="admin",
                is_active=True
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            print("✅ Admin user created successfully!")
            print(f"   User ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
            print(f"   Username: {admin_user.username}")
            print(f"   Role: {admin_user.role}")
            print(f"   Full Name: {admin_user.full_name}")
            print()
            print("⚠️  IMPORTANT: Store these credentials securely!")
            print(f"   Login URL: https://ar.company.com")
            print(f"   Email: {email}")
            print(f"   Password: {password}")

            return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        await engine.dispose()


def validate_password(password: str) -> bool:
    """Validate password meets security requirements."""
    if len(password) < 12:
        print("❌ Password must be at least 12 characters long")
        return False

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password)

    if not (has_upper and has_lower and has_digit and has_special):
        print("❌ Password must contain:")
        print("   - At least one uppercase letter")
        print("   - At least one lowercase letter")
        print("   - At least one digit")
        print("   - At least one special character (!@#$%^&* etc.)")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Create an admin user for AR Control Hub"
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Admin user email address"
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Admin username"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Admin password (min 12 chars, must contain upper, lower, digit, special)"
    )
    parser.add_argument(
        "--full-name",
        required=True,
        help="Admin user full name"
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Database URL (defaults to DATABASE_URL env var)"
    )

    args = parser.parse_args()

    # Validate password
    if not validate_password(args.password):
        sys.exit(1)

    # Get database URL
    database_url = args.database_url
    if not database_url:
        import os
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            print("   Set it or use --database-url parameter")
            sys.exit(1)

    print("🔐 Creating admin user...")
    print(f"   Email: {args.email}")
    print(f"   Username: {args.username}")
    print(f"   Full Name: {args.full_name}")
    print()

    # Create admin user
    success = asyncio.run(
        create_admin_user(
            email=args.email,
            username=args.username,
            password=args.password,
            full_name=args.full_name,
            database_url=database_url
        )
    )

    if success:
        print()
        print("✅ Admin user setup complete!")
        sys.exit(0)
    else:
        print()
        print("❌ Admin user creation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
