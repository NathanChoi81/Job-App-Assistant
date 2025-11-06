"""Database connection for worker"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from worker.config import settings

# Create async engine
engine = create_async_engine(
    settings.SUPABASE_URL.replace("https://", "postgresql+asyncpg://") + "/postgres",
    echo=False,
    pool_pre_ping=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db_session() -> AsyncSession:
    """Get database session (synchronous for Celery)"""
    return AsyncSessionLocal()

