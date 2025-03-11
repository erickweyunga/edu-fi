from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, String, Text, func
from sqlmodel import Field, Relationship, SQLModel

from models.base import LessonStatus
from models.user import User, Enrollment


class Lesson(SQLModel, table=True):
    """Lesson DB model"""

    __tablename__ = "lessons"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(255), index=True, nullable=False))
    description: Optional[str] = Field(sa_column=Column(Text))
    status: LessonStatus = Field(default=LessonStatus.DRAFT)
    content: Optional[str] = Field(sa_column=Column(Text))
    teacher_id: Optional[int] = Field(default=None, foreign_key="users.id")

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )

    # Relationships
    teacher: Optional[User] = Relationship(
        back_populates="lessons",
        sa_relationship_kwargs={"foreign_keys": "[Lesson.teacher_id]"},
    )
    students: List[Enrollment] = Relationship(back_populates="lesson")
    modules: List["Module"] = Relationship(back_populates="lesson")


class Module(SQLModel, table=True):
    """Module DB model - A section of a lesson"""

    __tablename__ = "modules"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String(255), nullable=False))
    order: int = Field(default=0)  # Order within the lesson
    content: Optional[str] = Field(sa_column=Column(Text))
    lesson_id: Optional[int] = Field(default=None, foreign_key="lessons.id")

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )

    # Relationships
    lesson: Optional[Lesson] = Relationship(back_populates="modules")
