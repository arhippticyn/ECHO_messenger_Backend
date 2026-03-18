from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import SECRET_KEY, ALGORITM
from app.models.user.user import User
from app.schemas.auth.auth import RegisterUser, LoginUser, UserResponse
from app.services.token import encode_token, get_current_user
from app.services.cookies import set_cookie
from app.db.session import get_db
from passlib.context import CryptContext
import bcrypt


router = APIRouter()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

@router.post('/register', response_model=UserResponse)
async def register(user: RegisterUser,res: Response, db: AsyncSession = Depends(get_db)):
    user_db = (await db.execute(select(User).where(User.username == user.username, User.email == user.email))).scalars().first()

    if user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already register')

   
    user_db = User(username=user.username, email=user.email, password=hash_password(user.password), provider='local', provider_id=user.username)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)

    payload = {
        'id': user_db.id,
        'username':user_db.username,
        'email': user_db.email 
    }

    access_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='access', exp=10)
    refresh_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='refresh', exp=1440)

    set_cookie(res, key='access', value=access_token)
    set_cookie(res, key='refresh', value=refresh_token)

    return user_db


@router.post('/login', response_model=UserResponse)
async def login(user: LoginUser, res: Response, db: AsyncSession = Depends(get_db)):
    user_db = (await db.execute(select(User).where(User.username == user.username))).scalars().first()

    if not user_db or user_db is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User is not found')
    
    if not verify_password(user.password, user_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Username or password is not correct')
    
    payload = {
        'id': user_db.id,
        'username':user_db.username,
        'email': user_db.email 
    }

    access_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='access', exp=10)
    refresh_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='refresh', exp=1440)

    set_cookie(res, value=access_token, key='access')
    set_cookie(res, value=refresh_token, key='refresh')

    return user_db
