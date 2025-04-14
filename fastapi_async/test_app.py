import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
import pytest_asyncio

from app import app
from db import Base, get_session
from models import User, Order

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


@pytest.fixture
def client(override_get_session):
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(override_get_session):
    from httpx import ASGITransport
    # 使用 ASGI Transport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_ping(async_client):
    response = await async_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


@pytest.mark.asyncio
async def test_sleep_endpoint(async_client):
    # Test that sleep_endpoint doesn't block for full 5 seconds
    # By setting a lower timeout and expecting it to complete
    start_time = asyncio.get_event_loop().time()
    response = await async_client.get("/sleep")
    elapsed = asyncio.get_event_loop().time() - start_time
    
    assert response.status_code == 200
    assert response.json() == {"message": "Woke up after 5 seconds"}
    assert elapsed >= 5.0  # Verify it waited at least 5 seconds


@pytest.mark.asyncio
async def test_create_user(async_client, setup_database):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = await async_client.post("/users/", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_get_users(async_client, setup_database):
    # Create test users first
    user_data = [
        {"username": "user1", "email": "user1@example.com", "password": "pass1"},
        {"username": "user2", "email": "user2@example.com", "password": "pass2"}
    ]
    
    for user in user_data:
        await async_client.post("/users/", json=user)
    
    # Test get users endpoint
    response = await async_client.get("/users/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["username"] == "user1"
    assert data[1]["username"] == "user2"


@pytest.mark.asyncio
async def test_create_order(async_client, setup_database):
    # Create a user first
    user_response = await async_client.post(
        "/users/", 
        json={"username": "orderuser", "email": "order@example.com", "password": "pass"}
    )
    user_id = user_response.json()["id"]
    
    # Create an order for the user
    order_data = {"amount": 99.99, "status": "pending"}
    response = await async_client.post(f"/users/{user_id}/orders/", json=order_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["amount"] == 99.99
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_create_order_nonexistent_user(async_client, setup_database):
    order_data = {"amount": 99.99}
    response = await async_client.post("/users/9999/orders/", json=order_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_get_orders(async_client, setup_database):
    # Create a user
    user_response = await async_client.post(
        "/users/", 
        json={"username": "ordersuser", "email": "orders@example.com", "password": "pass"}
    )
    user_id = user_response.json()["id"]
    
    # Create multiple orders
    order_data = [
        {"amount": 10.50, "status": "pending"},
        {"amount": 25.75, "status": "completed"}
    ]
    
    for order in order_data:
        await async_client.post(f"/users/{user_id}/orders/", json=order)
    
    # Test get orders endpoint
    response = await async_client.get("/orders/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert data[0]["amount"] == 10.50
    assert data[1]["amount"] == 25.75 