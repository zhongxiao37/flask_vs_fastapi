import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import pytest_asyncio

import sys
import os

# Add the parent directory to sys.path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from db import Base, get_session

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Override the get_session dependency to use the test database
@pytest.fixture(scope="function")
def override_get_session():
    async def _override_get_session():
        async with TestingSessionLocal() as session:
            yield session
    
    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def setup_database():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Clean up after test
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_session(setup_database):
    """提供用于测试的数据库会话"""
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def client(override_get_session, setup_database):
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(override_get_session, setup_database):
    # Use ASGI Transport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client 