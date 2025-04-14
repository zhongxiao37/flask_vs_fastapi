from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, Order
from fastapi import HTTPException
from typing import List, Optional


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """获取用户，如不存在返回None"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_order(db: AsyncSession, user_id: int, amount: float, status: str = "pending") -> Order:
    """创建订单业务逻辑"""
    # 检查用户是否存在
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 创建订单
    db_order = Order(user_id=user_id, amount=amount, status=status)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


async def get_all_orders(db: AsyncSession) -> List[Order]:
    """获取所有订单业务逻辑"""
    result = await db.execute(select(Order))
    return result.scalars().all()


async def get_order_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
    """根据ID获取订单"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order 