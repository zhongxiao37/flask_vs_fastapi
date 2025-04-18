from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import get_session
from models import User
from pydantic import BaseModel, ConfigDict
from typing import List
import logging

# 获取 logger
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session)):
    logger.info(f"Creating new user with username: {user.username}, email: {user.email}")
    
    # In a real app, hash the password
    db_user = User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    logger.info(f"User created successfully with ID: {db_user.id}")
    return db_user

@router.get("/", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_session)):
    logger.info("Retrieving all users")
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    logger.info(f"Retrieved {len(users)} users")
    return users 