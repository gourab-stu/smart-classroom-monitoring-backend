from fastapi import APIRouter
from app.routes import _auth


router = APIRouter(prefix="/api", tags=["API"])

router.include_router(router=_auth.router)
