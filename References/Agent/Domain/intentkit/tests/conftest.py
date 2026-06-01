import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testing.postgresql import Postgresql

from intentkit.config import db as db_module

os.environ.setdefault("REDIS_HOST", "localhost")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def postgresql_server():
    server = Postgresql()
    try:
        yield server
    finally:
        server.stop()


@pytest_asyncio.fixture(scope="session")
async def postgres_engine(postgresql_server):
    db_url = postgresql_server.url()
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(async_url)
    db_module.engine = engine
    try:
        yield engine
    finally:
        await engine.dispose()
        db_module.engine = None


async def _truncate_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result]
        if tables:
            table_names = ", ".join(f'"{table}"' for table in tables)
            await conn.execute(
                text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
            )


@pytest_asyncio.fixture()
async def db_engine(postgres_engine):
    await _truncate_tables(postgres_engine)
    try:
        yield postgres_engine
    finally:
        await _truncate_tables(postgres_engine)
