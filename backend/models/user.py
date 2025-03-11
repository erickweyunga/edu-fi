from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime, String, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel

from models.base import UserRole

# Handle forward references for type checking
if TYPE_CHECKING:
    from models.lesson import Lesson


# Define separate tables to avoid inheritance issues
class User(SQLModel, table=True):
    """User DB model"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        sa_column=Column(String, index=True, unique=True, nullable=False)
    )
    first_name: str
    last_name: str
    is_active: bool = True
    role: UserRole = Field(default=UserRole.STUDENT)
    hashed_password: str

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

    # Relationships - Use strings for forward references
    lessons: List["Lesson"] = Relationship(
        back_populates="teacher",
        sa_relationship_kwargs={"foreign_keys": "[Lesson.teacher_id]"},
    )
    enrolled_lessons: List["Enrollment"] = Relationship(back_populates="student")

    class Config:
        orm_mode = True
        from_attributes = True


# Junction table for many-to-many relationship between User and Lesson
class Enrollment(SQLModel, table=True):
    """Enrollment model - Student enrolled in a Lesson"""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "lesson_id", name="unique_enrollment"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: Optional[int] = Field(foreign_key="users.id")
    lesson_id: Optional[int] = Field(foreign_key="lessons.id")

    # Status of enrollment (active, completed, etc.)
    status: str = "active"

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

    # Relationships - Use strings for forward references
    student: Optional[User] = Relationship(back_populates="enrolled_lessons")
    lesson: Optional["Lesson"] = Relationship(back_populates="students")
