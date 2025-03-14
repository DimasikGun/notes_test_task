from typing import AsyncGenerator

import pytest
import sqlalchemy
from httpx import ASGITransport, AsyncClient
from pytest_asyncio import is_async_test
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.v1.auth.schemas import UserSchema
from core.config import settings
from core.database import Base
from core.database.db_helper import DatabaseHelper, db_helper
from main import main_app


def pytest_collection_modifyitems(items):
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture()
def password() -> str:
    return "StrongTestPassword123!"


@pytest.fixture()
def payload() -> dict[str, str]:
    return {"sub": "user123"}


@pytest.fixture(scope="session")
async def create_test_database() -> AsyncGenerator[None, None]:
    """Create test database if it doesn't exist."""
    admin_engine = create_async_engine(
        str(settings.db.test_admin_url), isolation_level="AUTOCOMMIT"
    )

    async with admin_engine.connect() as conn:
        await conn.execute(
            sqlalchemy.text(
                f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                f"FROM pg_stat_activity "
                f"WHERE pg_stat_activity.datname = '{settings.db.test_name}' "
                f"AND pid <> pg_backend_pid();"
            )
        )
        await conn.execute(
            sqlalchemy.text(f"DROP DATABASE IF EXISTS {settings.db.test_name}")
        )
        await conn.execute(sqlalchemy.text(f"CREATE DATABASE {settings.db.test_name}"))

    await admin_engine.dispose()

    yield


@pytest.fixture(scope="session")
async def test_db_helper(
    create_test_database: None,
) -> AsyncGenerator[DatabaseHelper, None]:
    """Initialize the database helper."""
    helper = DatabaseHelper(
        url=str(settings.db.test_url),
        echo=True,
        echo_pool=True,
        pool_size=3,
        max_overflow=5,
    )

    async with helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield helper

    async with helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await helper.dispose()


@pytest.fixture(scope="function")
async def db_session(
    test_db_helper: DatabaseHelper,
) -> AsyncGenerator[AsyncSession, None]:
    """Get database session for tests."""
    async with test_db_helper.factory() as session:
        yield session
        await session.rollback()


@pytest.fixture()
def user_schema_in() -> UserSchema:
    return UserSchema(username="user123", password="StrongTestPassword123!")


@pytest.fixture()
def user_dict_in_weak_pass() -> dict:
    return {"username": "user123", "password": "weak"}


@pytest.fixture(scope="function")
async def api_client(test_db_helper) -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as api_client:
        main_app.dependency_overrides[db_helper.session_getter] = (
            test_db_helper.session_getter
        )
        yield api_client
