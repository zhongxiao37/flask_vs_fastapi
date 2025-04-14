import pytest
import pytest_asyncio
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from models import User, Order
from services import orders as orders_service


@pytest_asyncio.fixture
async def test_user(setup_database, test_session):
    """创建测试用户"""
    # 创建用户
    user = User(username="testuser", email="test@example.com", hashed_password="testpass")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


class TestOrdersService:
    """订单服务测试类"""
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_existing(self, test_session, test_user):
        """测试获取存在的用户"""
        user = await orders_service.get_user_by_id(db=test_session, user_id=test_user.id)
        assert user is not None
        assert user.id == test_user.id
        assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_nonexistent(self, test_session):
        """测试获取不存在的用户"""
        user = await orders_service.get_user_by_id(db=test_session, user_id=9999)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_create_order_success(self, test_session, test_user):
        """测试成功创建订单"""
        order = await orders_service.create_order(
            db=test_session, 
            user_id=test_user.id,
            amount=100.0,
            status="pending"
        )
        
        assert order is not None
        assert order.id is not None
        assert order.user_id == test_user.id
        assert order.amount == 100.0
        assert order.status == "pending"
    
    @pytest.mark.asyncio
    async def test_create_order_nonexistent_user(self, test_session):
        """测试创建订单但用户不存在"""
        with pytest.raises(HTTPException) as excinfo:
            await orders_service.create_order(
                db=test_session, 
                user_id=9999,
                amount=100.0
            )
        
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "User not found"
    
    @pytest.mark.asyncio
    async def test_get_all_orders_empty(self, test_session):
        """测试获取所有订单（空）"""
        orders = await orders_service.get_all_orders(db=test_session)
        assert len(orders) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_orders(self, test_session, test_user):
        """测试获取所有订单"""
        # 创建两个测试订单
        order1 = Order(user_id=test_user.id, amount=50.0, status="pending")
        order2 = Order(user_id=test_user.id, amount=75.0, status="completed")
        test_session.add_all([order1, order2])
        await test_session.commit()
        
        orders = await orders_service.get_all_orders(db=test_session)
        assert len(orders) == 2
        assert orders[0].amount == 50.0
        assert orders[1].amount == 75.0
    
    @pytest.mark.asyncio
    async def test_get_order_by_id(self, test_session, test_user):
        """测试通过ID获取订单"""
        # 创建测试订单
        order = Order(user_id=test_user.id, amount=120.0, status="processing")
        test_session.add(order)
        await test_session.commit()
        await test_session.refresh(order)
        
        found_order = await orders_service.get_order_by_id(db=test_session, order_id=order.id)
        assert found_order is not None
        assert found_order.id == order.id
        assert found_order.amount == 120.0
        assert found_order.status == "processing"
    
    @pytest.mark.asyncio
    async def test_get_order_by_id_nonexistent(self, test_session):
        """测试通过ID获取不存在的订单"""
        with pytest.raises(HTTPException) as excinfo:
            await orders_service.get_order_by_id(db=test_session, order_id=9999)
        
        assert excinfo.value.status_code == 404
        assert excinfo.value.detail == "Order not found" 