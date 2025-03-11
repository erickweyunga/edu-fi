from typing import Any, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from api.deps import (
    get_current_active_user,
    get_current_teacher_or_admin_user,
    get_db,
)
from models.lesson import LessonStatus
from models.user import User
from schemas.lesson import (
    EnrollmentCreate,
    EnrollmentResponse,
    LessonCreate,
    LessonDetailResponse,
    LessonResponse,
    LessonUpdate,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
)

router = APIRouter()


@router.get("", response_model=List[LessonResponse])
async def read_lessons(
    skip: int = 0,
    limit: int = 100,
    status: LessonStatus = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve lessons
    """
    # Filter by status if provided
    if status:
        # TODO: Implement status filtering
        pass
    
    # Regular users (students) can only see published lessons
    if current_user.role == "student":
        # TODO: Implement status filtering
        pass
    
    lessons = await crud.lesson.get_multi(db, skip=skip, limit=limit)
    return lessons


@router.post("", response_model=LessonResponse)
async def create_lesson(
    lesson_in: LessonCreate,
    current_user: User = Depends(get_current_teacher_or_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new lesson (teachers and admins only)
    """
    lesson = await crud.lesson.create_with_teacher(
        db, obj_in=lesson_in, teacher_id=current_user.id
    )
    return lesson


@router.get("/teacher", response_model=List[LessonResponse])
async def read_teacher_lessons(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_teacher_or_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get lessons created by current teacher
    """
    lessons = await crud.lesson.get_teacher_lessons(
        db, teacher_id=current_user.id, skip=skip, limit=limit
    )
    return lessons


@router.get("/enrolled", response_model=List[LessonResponse])
async def read_enrolled_lessons(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get lessons the current user is enrolled in
    """
    lessons = await crud.lesson.get_student_lessons(
        db, student_id=current_user.id, skip=skip, limit=limit
    )
    return lessons


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def read_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a specific lesson by id
    """
    lesson = await crud.lesson.get_lesson_with_details(db, lesson_id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Student can only access published lessons or ones they're enrolled in
    if (
        current_user.role == "student"
        and lesson.status != LessonStatus.PUBLISHED
        and not await crud.lesson.is_enrolled(
            db, lesson_id=lesson_id, student_id=current_user.id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # Get student count
    student_count = await crud.lesson.get_student_count(db, lesson_id=lesson_id)
    
    # Combine everything into a response
    response = lesson.__dict__.copy()
    response["student_count"] = student_count
    
    return response


@router.patch("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_in: LessonUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a lesson
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Only the teacher who created the lesson or an admin can update it
    if (
        lesson.teacher_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    lesson = await crud.lesson.update(db, db_obj=lesson, obj_in=lesson_in)
    return lesson


@router.delete("/{lesson_id}", response_model=LessonResponse)
async def delete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete a lesson
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Only the teacher who created the lesson or an admin can delete it
    if (
        lesson.teacher_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    lesson = await crud.lesson.remove(db, id=lesson_id)
    return lesson


# Module routes
@router.post("/{lesson_id}/modules", response_model=ModuleResponse)
async def create_module(
    lesson_id: int,
    module_in: ModuleCreate,
    current_user: User = Depends(get_current_teacher_or_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new module for a lesson
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Only the teacher who created the lesson or an admin can add modules
    if (
        lesson.teacher_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    module = await crud.module.create_with_lesson(
        db, obj_in=module_in, lesson_id=lesson_id
    )
    return module


@router.get("/{lesson_id}/modules", response_model=List[ModuleResponse])
async def read_modules(
    lesson_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get modules for a lesson
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Student can only access published lessons or ones they're enrolled in
    if (
        current_user.role == "student"
        and lesson.status != LessonStatus.PUBLISHED
        and not await crud.lesson.is_enrolled(
            db, lesson_id=lesson_id, student_id=current_user.id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    modules = await crud.module.get_lesson_modules(
        db, lesson_id=lesson_id, skip=skip, limit=limit
    )
    return modules


@router.patch("/{lesson_id}/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    lesson_id: int,
    module_id: int,
    module_in: ModuleUpdate,
    current_user: User = Depends(get_current_teacher_or_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a module
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Only the teacher who created the lesson or an admin can update modules
    if (
        lesson.teacher_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    module = await crud.module.get(db, id=module_id)
    if not module or module.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )
    
    module = await crud.module.update(db, db_obj=module, obj_in=module_in)
    return module


@router.delete("/{lesson_id}/modules/{module_id}", response_model=ModuleResponse)
async def delete_module(
    lesson_id: int,
    module_id: int,
    current_user: User = Depends(get_current_teacher_or_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Delete a module
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Only the teacher who created the lesson or an admin can delete modules
    if (
        lesson.teacher_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    module = await crud.module.get(db, id=module_id)
    if not module or module.lesson_id != lesson_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )
    
    module = await crud.module.remove(db, id=module_id)
    return module


# Enrollment routes
@router.post("/{lesson_id}/enroll", response_model=EnrollmentResponse)
async def enroll_in_lesson(
    lesson_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Enroll current user in a lesson
    """
    lesson = await crud.lesson.get(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Students can only enroll in published lessons
    if (
        current_user.role == "student"
        and lesson.status != LessonStatus.PUBLISHED
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lesson is not published",
        )
    
    enrollment = await crud.enrollment.enroll_student(
        db, student_id=current_user.id, lesson_id=lesson_id
    )
    
    # Add background task to send enrollment notification
    # background_tasks.add_task(send_enrollment_notification, enrollment.id)
    
    return enrollment