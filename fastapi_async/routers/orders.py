from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session
from models import User, Order
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# Pydantic models for request/response
class OrderCreate(BaseModel):
    user_id: int
    amount: float
    status: Optional[str] = "pending"

class OrderResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    status: str
    
    model_config = ConfigDict(from_attributes=True)

# Create router
router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_session)):
    # Check if user exists
    result = await db.execute(select(User).where(User.id == order.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_order = Order(user_id=order.user_id, amount=order.amount, status=order.status)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return orders 