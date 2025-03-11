from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from crud.base import CRUDBase
from models.lesson import Lesson, Module
from models.user import Enrollment, User
from schemas.lesson import LessonCreate, LessonUpdate, ModuleCreate, ModuleUpdate


class CRUDLesson(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    """CRUD operations for Lesson model"""

    async def create_with_teacher(
        self, db: AsyncSession, *, obj_in: LessonCreate, teacher_id: int
    ) -> Lesson:
        """Create new lesson with teacher"""
        lesson = Lesson(
            title=obj_in.title,
            description=obj_in.description,
            status=obj_in.status,
            content=obj_in.content,
            teacher_id=teacher_id,
        )
        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)
        return lesson

    async def get_teacher_lessons(
        self, db: AsyncSession, *, teacher_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lesson]:
        """Get lessons by teacher"""
        statement = (
            select(Lesson)
            .where(Lesson.teacher_id == teacher_id)
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement)
        return results.scalars().all()

    async def get_lesson_with_details(
        self, db: AsyncSession, *, lesson_id: int
    ) -> Optional[Lesson]:
        """Get lesson with teacher and modules"""
        statement = (
            select(Lesson)
            .where(Lesson.id == lesson_id)
            .options(
                joinedload(Lesson.teacher),
                joinedload(Lesson.modules),
            )
        )
        results = await db.execute(statement)
        return results.scalar_one_or_none()

    async def get_student_lessons(
        self, db: AsyncSession, *, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Lesson]:
        """Get lessons enrolled by student"""
        statement = (
            select(Lesson)
            .join(Enrollment, Lesson.id == Enrollment.lesson_id)
            .where(Enrollment.student_id == student_id)
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement)
        return results.scalars().all()

    async def get_student_count(self, db: AsyncSession, *, lesson_id: int) -> int:
        """Get number of students enrolled in a lesson"""
        statement = select(func.count(Enrollment.id)).where(
            Enrollment.lesson_id == lesson_id
        )
        result = await db.execute(statement)
        return result.scalar_one()

    async def is_teacher(
        self, db: AsyncSession, *, lesson_id: int, user_id: int
    ) -> bool:
        """Check if user is the teacher of the lesson"""
        statement = select(Lesson).where(
            Lesson.id == lesson_id, Lesson.teacher_id == user_id
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none() is not None

    async def is_enrolled(
        self, db: AsyncSession, *, lesson_id: int, student_id: int
    ) -> bool:
        """Check if student is enrolled in the lesson"""
        statement = select(Enrollment).where(
            Enrollment.lesson_id == lesson_id, Enrollment.student_id == student_id
        )
        result = await db.execute(statement)
        return result.scalar_one_or_none() is not None


class CRUDModule(CRUDBase[Module, ModuleCreate, ModuleUpdate]):
    """CRUD operations for Module model"""

    async def create_with_lesson(
        self, db: AsyncSession, *, obj_in: ModuleCreate, lesson_id: int
    ) -> Module:
        """Create new module for a lesson"""
        module = Module(
            title=obj_in.title,
            order=obj_in.order,
            content=obj_in.content,
            lesson_id=lesson_id,
        )
        db.add(module)
        await db.commit()
        await db.refresh(module)
        return module

    async def get_lesson_modules(
        self, db: AsyncSession, *, lesson_id: int, skip: int = 0, limit: int = 100
    ) -> List[Module]:
        """Get modules by lesson"""
        statement = (
            select(Module)
            .where(Module.lesson_id == lesson_id)
            .order_by(Module.order)
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement)
        return results.scalars().all()


class CRUDEnrollment(CRUDBase[Enrollment, None, None]):
    """CRUD operations for Enrollment model"""

    async def enroll_student(
        self, db: AsyncSession, *, student_id: int, lesson_id: int
    ) -> Enrollment:
        """Enroll student in lesson"""
        # Check if already enrolled
        statement = select(Enrollment).where(
            Enrollment.student_id == student_id, Enrollment.lesson_id == lesson_id
        )
        result = await db.execute(statement)
        enrollment = result.scalar_one_or_none()

        if enrollment:
            # If previously enrolled but with different status, update status
            if enrollment.status != "active":
                enrollment.status = "active"
                db.add(enrollment)
                await db.commit()
                await db.refresh(enrollment)
            return enrollment

        # Create new enrollment
        enrollment = Enrollment(
            student_id=student_id, lesson_id=lesson_id, status="active"
        )
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    async def update_status(
        self, db: AsyncSession, *, enrollment_id: int, status: str
    ) -> Optional[Enrollment]:
        """Update enrollment status"""
        enrollment = await self.get(db, id=enrollment_id)
        if not enrollment:
            return None

        enrollment.status = status
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    async def get_student_enrollments(
        self, db: AsyncSession, *, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        """Get enrollments by student"""
        statement = (
            select(Enrollment)
            .where(Enrollment.student_id == student_id)
            .options(joinedload(Enrollment.lesson))
            .offset(skip)
            .limit(limit)
        )
        results = await db.execute(statement)
        return results.scalars().all()


lesson = CRUDLesson(Lesson)
module = CRUDModule(Module)
enrollment = CRUDEnrollment(Enrollment)
