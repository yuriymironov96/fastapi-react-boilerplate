import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.db import Base, DatabaseSessionManager


@pytest.fixture(scope="function")
async def test_db_session() -> AsyncSession:
    """Create a test database session with an in-memory SQLite database."""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session_manager() -> DatabaseSessionManager:
    """Create a test database session manager."""
    # Use in-memory SQLite for testing
    manager = DatabaseSessionManager(
        "sqlite+aiosqlite:///:memory:",
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
            "echo": False,
        },
    )

    async with manager.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield manager

    async with manager.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await manager.close()
