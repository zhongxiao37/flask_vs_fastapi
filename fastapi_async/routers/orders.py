from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_session
from models import Order
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from services import orders as orders_service

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
    """创建新订单"""
    return await orders_service.create_order(
        db=db, 
        user_id=order.user_id, 
        amount=order.amount, 
        status=order.status
    )

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_session)):
    """获取所有订单"""
    return await orders_service.get_all_orders(db=db)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: AsyncSession = Depends(get_session)):
    """根据ID获取订单"""
    return await orders_service.get_order_by_id(db=db, order_id=order_id) 