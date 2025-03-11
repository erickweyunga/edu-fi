from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models.user import UserRole


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool = True
    role: UserRole = UserRole.STUDENT


# Create request schemas
class UserCreate(UserBase):
    password: str = Field(min_length=8)


# Update request schemas
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)


# Response schemas
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


# User with additional info for admin views
class UserDetailResponse(UserResponse):
    pass


# Current user info
class CurrentUser(UserResponse):
    pass
