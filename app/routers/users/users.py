from fastapi import APIRouter, Depends, HTTPException, status
from ...db.session import get_db
from ...models.user.user import User
from ...schemas.auth.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from ...services.token import get_current_user
from sqlalchemy import select


router = APIRouter()

@router.get('', response_model=list[UserResponse])
async def get_users_by_search(search: str | None = None,user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id != user.id)

    if search:
        query = query.where(User.username.ilike(f'%{search}%'))  # частичный поиск

    users = (await db.execute(query)).scalars().all()
    return users


@router.get('/{id}', response_model=UserResponse)
async def get_user_by_id(id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.id != user.id, User.id == id))).scalars().first()

    return user