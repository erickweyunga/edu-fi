from fastapi import APIRouter

from api.routes import auth, lessons, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])