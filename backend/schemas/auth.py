from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token schema"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: Optional[str] = None
    exp: Optional[int] = None


class Login(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordUpdate(BaseModel):
    """Password update request schema"""
    current_password: str
    new_password: str