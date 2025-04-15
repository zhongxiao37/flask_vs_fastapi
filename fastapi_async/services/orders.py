from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, Order
from fastapi import HTTPException
from typing import List, Optional
import logging

# 获取 logger
logger = logging.getLogger(__name__)

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """获取用户，如不存在返回None"""
    logger.info(f"Looking up user with ID: {user_id}")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user:
        logger.info(f"Found user with ID: {user_id}")
    else:
        logger.warning(f"User with ID: {user_id} not found")
    
    return user


async def create_order(db: AsyncSession, user_id: int, amount: float, status: str = "pending") -> Order:
    """创建订单业务逻辑"""
    logger.info(f"Creating order for user_id: {user_id}, amount: {amount}, status: {status}")
    
    # 检查用户是否存在
    user = await get_user_by_id(db, user_id)
    if not user:
        logger.error(f"Failed to create order: User with ID {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    # 创建订单
    db_order = Order(user_id=user_id, amount=amount, status=status)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    
    logger.info(f"Order created successfully with ID: {db_order.id}")
    return db_order


async def get_all_orders(db: AsyncSession) -> List[Order]:
    """获取所有订单业务逻辑"""
    logger.info("Retrieving all orders from database")
    
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    
    logger.info(f"Retrieved {len(orders)} orders from database")
    return orders


async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """根据ID获取订单"""
    logger.info(f"Looking up order with ID: {order_id}")
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    
    if not order:
        logger.error(f"Order with ID: {order_id} not found")
        raise HTTPException(status_code=404, detail="Order not found")
    
    logger.info(f"Found order with ID: {order_id}")
    return order 