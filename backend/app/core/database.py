from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy import text
from app.core.config import settings
from app import models as app_models

engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug, # desativar em prod
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()

async def init_db() -> None:
    # Garante registro dos models na metadata para Alembic/autogenerate
    _ = app_models

    # Estratégia oficial: schema é gerenciado por Alembic (sem create_all no startup)
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

async def close_db() -> None:
    await engine.dispose()

async def transaction_context():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session
