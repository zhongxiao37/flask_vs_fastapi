import pytest
from fastapi.testclient import TestClient
from models import User, Order


class TestOrderEndpoints:
    """订单 API 端点测试类"""
    
    @pytest.mark.asyncio
    async def test_create_order(self, async_client, setup_database, test_session):
        """测试创建订单 API"""
        # 先创建用户
        user = User(username="testuser", email="test@example.com", hashed_password="testpass")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # 发送创建订单请求
        order_data = {
            "user_id": user.id,
            "amount": 123.45,
            "status": "pending"
        }
        
        response = await async_client.post("/orders/", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == user.id
        assert data["amount"] == 123.45
        assert data["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_create_order_nonexistent_user(self, async_client, setup_database):
        """测试创建订单但用户不存在 API"""
        order_data = {
            "user_id": 9999,  # 不存在的用户ID
            "amount": 123.45
        }
        
        response = await async_client.post("/orders/", json=order_data)
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"
    
    @pytest.mark.asyncio
    async def test_get_orders(self, async_client, setup_database, test_session):
        """测试获取所有订单 API"""
        # 创建用户
        user = User(username="testuser", email="test@example.com", hashed_password="testpass")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # 创建订单
        orders = [
            Order(user_id=user.id, amount=10.99, status="pending"),
            Order(user_id=user.id, amount=20.99, status="completed")
        ]
        test_session.add_all(orders)
        await test_session.commit()
        
        # 获取所有订单
        response = await async_client.get("/orders/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["amount"] == 10.99
        assert data[1]["amount"] == 20.99
    
    @pytest.mark.asyncio
    async def test_get_order_by_id(self, async_client, setup_database, test_session):
        """测试通过 ID 获取订单 API"""
        # 创建用户
        user = User(username="testuser", email="test@example.com", hashed_password="testpass")
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # 创建订单
        order = Order(user_id=user.id, amount=99.99, status="processing")
        test_session.add(order)
        await test_session.commit()
        await test_session.refresh(order)
        
        # 通过 ID 获取订单
        response = await async_client.get(f"/orders/{order.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == order.id
        assert data["amount"] == 99.99
        assert data["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_nonexistent(self, async_client, setup_database):
        """测试通过不存在的 ID 获取订单 API"""
        response = await async_client.get("/orders/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Order not found" 