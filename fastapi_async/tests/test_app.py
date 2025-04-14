import pytest
import asyncio
from sqlalchemy import select, delete
import pytest_asyncio

import sys
import os

# Add the parent directory to sys.path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import User, Order


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