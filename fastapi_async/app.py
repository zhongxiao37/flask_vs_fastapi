from fastapi import FastAPI, Depends, HTTPException
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session, engine, Base
from models import User, Order
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup and shutdown logic
    # We no longer need to create tables here since we'll use Alembic migrations
    yield

app = FastAPI(lifespan=lifespan)

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    amount: float
    status: Optional[str] = "pending"

class OrderResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    status: str
    
    class Config:
        orm_mode = True

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/sleep")
async def sleep_endpoint():
    await asyncio.sleep(5)  # 异步 sleep，不会阻塞其他请求
    return {"message": "Woke up after 5 seconds"}

# User endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    # In a real app, hash the password
    db_user = User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# Order endpoints
@app.post("/users/{user_id}/orders/", response_model=OrderResponse)
async def create_order(user_id: int, order: OrderCreate, db: AsyncSession = Depends(get_session)):
    # Check if user exists
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_order = Order(user_id=user_id, amount=order.amount, status=order.status)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order

@app.get("/orders/", response_model=List[OrderResponse])
async def get_orders(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Order))
    orders = result.scalars().all()
    return orders

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)