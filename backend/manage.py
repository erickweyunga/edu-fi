#!/usr/bin/env python
import argparse
import subprocess
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import project modules
sys.path.insert(0, str(Path(__file__).parent))
# from core.db import init_db


def run_alembic(args):
    """Run Alembic with the specified arguments"""
    alembic_args = ["alembic"] + args
    return subprocess.run(alembic_args, check=True)


# async def init_database():
#     """Initialize database tables using SQLModel metadata"""
#     print("Initializing database tables...")
#     await init_db()
#     print("Database tables initialized successfully.")


def main():
    """Main entry point for the management script"""
    parser = argparse.ArgumentParser(description="Edu-Fi Backend Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run development server
    run_parser = subparsers.add_parser("run", help="Run development server")
    run_parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind the server to"
    )
    run_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    run_parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management commands")
    db_subparsers = db_parser.add_subparsers(
        dest="db_command", help="DB Command to run"
    )

    # Initialize database
    db_subparsers.add_parser("init", help="Initialize database tables")

    # Create migration
    migrate_parser = db_subparsers.add_parser("migrate", help="Create a new migration")
    migrate_parser.add_argument(
        "--message", "-m", required=True, help="Migration message"
    )
    migrate_parser.add_argument(
        "--autogenerate", "-a", action="store_true", help="Auto-generate migration"
    )

    # Upgrade database
    upgrade_parser = db_subparsers.add_parser("upgrade", help="Upgrade database schema")
    upgrade_parser.add_argument(
        "--revision", default="head", help="Revision to upgrade to (default: head)"
    )

    # Downgrade database
    downgrade_parser = db_subparsers.add_parser(
        "downgrade", help="Downgrade database schema"
    )
    downgrade_parser.add_argument(
        "--revision", required=True, help="Revision to downgrade to"
    )

    # Reset database
    db_subparsers.add_parser(
        "reset", help="Reset database (drop all tables and recreate)"
    )

    # Create superuser
    user_parser = subparsers.add_parser("user", help="User management commands")
    user_subparsers = user_parser.add_subparsers(
        dest="user_command", help="User Command to run"
    )

    # Create superuser command
    createsuperuser_parser = user_subparsers.add_parser(
        "createsuperuser", help="Create a superuser account"
    )
    createsuperuser_parser.add_argument("--email", required=True, help="User email")
    createsuperuser_parser.add_argument(
        "--password", required=True, help="User password"
    )
    createsuperuser_parser.add_argument(
        "--first-name", required=True, help="User first name"
    )
    createsuperuser_parser.add_argument(
        "--last-name", required=True, help="User last name"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "run":
        uvicorn.run(
            "main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
    elif args.command == "db":
        if not args.db_command:
            db_parser.print_help()
            return

        # if args.db_command == "init":
        #     asyncio.run(init_database())
        if args.db_command == "migrate":
            alembic_args = ["revision"]
            if args.autogenerate:
                alembic_args.append("--autogenerate")
            alembic_args.extend(["-m", args.message])
            run_alembic(alembic_args)
        elif args.db_command == "upgrade":
            run_alembic(["upgrade", args.revision])
        elif args.db_command == "downgrade":
            run_alembic(["downgrade", args.revision])
        elif args.db_command == "reset":
            confirm = input(
                "This will delete all data in your database. Are you sure? [y/N] "
            )
            if confirm.lower() == "y":
                run_alembic(["downgrade", "base"])
                run_alembic(["upgrade", "head"])
                print("Database has been reset.")
            else:
                print("Operation cancelled.")
    elif args.command == "user":
        if not args.user_command:
            user_parser.print_help()
            return

        if args.user_command == "createsuperuser":
            # Import here to avoid circular imports
            import asyncio
            from sqlalchemy.ext.asyncio import AsyncSession

            from core.db import async_session
            from crud import user as user_crud
            from models.user import UserRole
            from schemas.user import UserCreate

            async def create_superuser():
                async with async_session() as db:
                    db_session = db
                    user_data = UserCreate(
                        email=args.email,
                        password=args.password,
                        first_name=args.first_name,
                        last_name=args.last_name,
                        is_active=True,
                        role=UserRole.ADMIN,
                    )

                    # Check if user already exists
                    existing_user = await user_crud.get_by_email(
                        db=db_session, email=args.email
                    )
                    if existing_user:
                        print(f"User with email {args.email} already exists.")
                        return

                    # Create user
                    user = await user_crud.create(db=db_session, obj_in=user_data)
                    print(f"Superuser {user.email} created successfully.")

            asyncio.run(create_superuser())


if __name__ == "__main__":
    main()
