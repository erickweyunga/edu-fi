from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from api.deps import (
    get_current_active_user,
    get_current_admin_user,
    get_db,
)
from models.user import User
from schemas.user import (
    CurrentUser,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter()


@router.get("/me", response_model=CurrentUser)
async def read_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update current user
    """
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve users (admin only)
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new user (admin only)
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    user = await crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserDetailResponse)
async def read_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific user by id
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Only admin can access other users data
    if user.id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a user (admin only)
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete a user (admin only)
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user = await crud.user.remove(db, id=user_id)
    return user
