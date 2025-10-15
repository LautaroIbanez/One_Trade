"""
Database configuration and session management.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Database engine
def get_database_url():
    """Get the appropriate database URL based on configuration."""
    if settings.USE_SQLITE:
        return settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    else:
        return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    get_database_url(),
    echo=settings.ENVIRONMENT == "development",
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
class Base(DeclarativeBase):
    """Base class for all database models."""
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from app.models import recommendation, market_data, backtest  # noqa
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

