"""Database connection and session management"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

logger = structlog.get_logger()

# Get database URL - DATABASE_URL is required for proper database connection
if not settings.DATABASE_URL:
    error_msg = (
        "DATABASE_URL environment variable is not set. "
        "Please set it in Fly.io secrets with: "
        "flyctl secrets set DATABASE_URL='postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres' -a job-app-assistant-api"
    )
    logger.error(error_msg)
    raise ValueError(error_msg)

database_url = settings.DATABASE_URL
# Convert to asyncpg format if needed
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not database_url.startswith("postgresql+asyncpg://"):
    # If it doesn't start with postgresql://, assume it needs the prefix
    database_url = f"postgresql+asyncpg://{database_url}"

logger.info("Connecting to database", url=database_url[:50] + "..." if len(database_url) > 50 else database_url)

# Create async engine with connection timeouts
engine = create_async_engine(
    database_url,
    echo=not settings.is_production,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    poolclass=NullPool if settings.is_production else None,  # Use NullPool in production to avoid connection issues
    connect_args={
        "server_settings": {
            "application_name": "job-app-assistant-api",
        },
        "command_timeout": 10,  # 10 second timeout for queries
    },
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

