"""
Pytest configuration fixtures for QI-Guard Async Integration Testing.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base, get_db
from app.core.security import generate_api_key, hash_api_key
from app.models.project import Project, AccessTier
from app.models.api_key import APIKey, KeyType
from app.main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    """Recreates database schema for each test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def seed_data(db_session: AsyncSession):
    """Seeds test project and API keys."""
    project = Project(name="Test Project", tier=AccessTier.DEVELOPER)
    db_session.add(project)
    await db_session.flush()

    raw_live, prefix_live, hash_live = generate_api_key("live")
    live_key = APIKey(
        project_id=project.id,
        key_prefix=prefix_live,
        hashed_key=hash_live,
        key_type=KeyType.LIVE,
        name="Live Key"
    )
    db_session.add(live_key)

    raw_test, prefix_test, hash_test = generate_api_key("test")
    test_key = APIKey(
        project_id=project.id,
        key_prefix=prefix_test,
        hashed_key=hash_test,
        key_type=KeyType.TEST,
        name="Test Key"
    )
    db_session.add(test_key)

    await db_session.commit()

    return {
        "project": project,
        "raw_live_key": raw_live,
        "raw_test_key": raw_test,
    }


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()
