from fastapi import APIRouter, Depends
from ...services.token import get_current_user
from ...models.user.user import User
from ...schemas.auth.auth import UserResponse

router = APIRouter()

@router.get('/me', response_model=UserResponse)
async def read_user(user: User = Depends(get_current_user)):
    return user