"""Asynchronous database connection and session management."""

from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging import logger


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy entities."""
    pass


# Ensure data directory exists if SQLite is used
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    parent_dir = Path(db_path).parent
    parent_dir.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initializes tables for local development and seeds standard presets."""
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default schema presets
    from app.infrastructure.models import (
        Organization,
        SchemaDefinition,
        User,
        UserRole,
        organization_memberships,
    )
    from app.infrastructure.presets import DEFAULT_SCHEMA_PRESETS
    from app.core.config import settings
    from app.core.security import hash_password
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(select(SchemaDefinition).limit(1))
        existing = result.scalar_one_or_none()
        if not existing:
            logger.info("Seeding default business schema presets...")
            for p in DEFAULT_SCHEMA_PRESETS:
                schema_def = SchemaDefinition(
                    id=p["id"],
                    organization_id="default-org",
                    name=p["name"],
                    description=p["description"],
                    document_type=p["document_type"],
                    fields_config_json=p["fields_config_json"],
                )
                session.add(schema_def)
            await session.commit()
            logger.info("Default schema presets seeded successfully.")

        # Seed default organization
        result_org = await session.execute(
            select(Organization).where(Organization.id == settings.DEFAULT_ADMIN_ORG)
        )
        if not result_org.scalar_one_or_none():
            logger.info("Seeding default organization...")
            session.add(
                Organization(id=settings.DEFAULT_ADMIN_ORG, name="Organización Principal")
            )
            await session.commit()
            logger.info("Default organization seeded successfully.")

        # Seed default admin user (local development bootstrap)
        result_user = await session.execute(select(User).limit(1))
        if not result_user.scalar_one_or_none():
            logger.info("Seeding default admin user for local development...")
            admin = User(
                organization_id=settings.DEFAULT_ADMIN_ORG,
                email=settings.DEFAULT_ADMIN_EMAIL,
                hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            await session.execute(
                organization_memberships.insert().values(
                    user_id=admin.id,
                    organization_id=settings.DEFAULT_ADMIN_ORG,
                )
            )
            await session.commit()
            logger.info(
                "Default admin created: %s (change the default password in production).",
                settings.DEFAULT_ADMIN_EMAIL,
            )

    logger.info("Database initialized successfully.")
