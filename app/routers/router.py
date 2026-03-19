from fastapi import APIRouter
from .auth.auth import router as auth_router
from .profile.profile import router as profile_router
from .users.users import router as users_router

router = APIRouter()

router.include_router(
    router=auth_router,
    prefix='/auth',
    tags=['Auth']
)

router.include_router(
    router=profile_router,
    prefix='/profile',
    tags=['Profile']
)

router.include_router(
    router=users_router,
    prefix='/users',
    tags=['Users']
)