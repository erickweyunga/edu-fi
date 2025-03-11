from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from models.lesson import LessonStatus
from schemas.user import UserResponse


# Module schemas
class ModuleBase(BaseModel):
    title: str
    order: int = 0
    content: Optional[str] = None


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None
    content: Optional[str] = None


class ModuleResponse(ModuleBase):
    id: int
    lesson_id: int
    created_at: datetime
    updated_at: datetime


# Lesson schemas
class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: LessonStatus = LessonStatus.DRAFT
    content: Optional[str] = None


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[LessonStatus] = None
    content: Optional[str] = None


class LessonResponse(LessonBase):
    id: int
    teacher_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class LessonDetailResponse(LessonResponse):
    teacher: Optional[UserResponse] = None
    modules: List[ModuleResponse] = []
    student_count: int = 0


# Enrollment schemas
class EnrollmentCreate(BaseModel):
    lesson_id: int


class EnrollmentUpdate(BaseModel):
    status: str


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    lesson_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    lesson: Optional[LessonResponse] = None
