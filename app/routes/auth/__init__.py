from fastapi import APIRouter
from .student import router as student_router
from .teacher import router as teacher_router

router = APIRouter(prefix="/auth")

router.include_router(student_router)
router.include_router(teacher_router)
