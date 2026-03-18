from fastapi import APIRouter
from .auth.auth import router as auth_router

router = APIRouter()

router.include_router(
    router=auth_router,
    prefix='/auth',
    tags=['Auth']
)