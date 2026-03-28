from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
import app.models
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import SECRET_KEY, ALGORITM, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, DEBUG, FRONTEND_URL
from app.models.user.user import User
from app.schemas.auth.auth import RegisterUser, LoginUser, UserResponse
from app.services.token import encode_token, verify_token
from app.services.cookies import set_cookie
from app.db.session import get_db
from passlib.context import CryptContext
import bcrypt
from authlib.integrations.starlette_client import OAuth


router = APIRouter()

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

@router.post('/register', response_model=UserResponse)
async def register(user: RegisterUser,res: Response, db: AsyncSession = Depends(get_db)):
    user_db = (await db.execute(select(User).where(User.username == user.username, User.email == user.email))).scalars().first()

    if user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already register')

   
    user_db = User(username=user.username, email=user.email, password=hash_password(user.password), provider='local', provider_id=user.username, is_online=True)
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

@router.get('/google')
async def google_login(request: Request):
    redirect_uri = None
    if DEBUG:
        redirect_uri = 'http://127.0.0.1:8024/auth/google/callback'
    else:
        redirect_uri = 'https://echo-bj2n.onrender.com/auth/google/callback'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/google/callback')
async def google_callback(request: Request,res: Response, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token['userinfo']

    email = user_info['email']
    username = user_info['email'].split('@')[0]
    provider = 'google'
    provider_id = user_info['sub']

    user_local_provider = (await db.execute(select(User).where(User.provider == 'local', User.email == email))).scalars().first()

    if user_local_provider:
        if DEBUG:
            return RedirectResponse(url=FRONTEND_URL)

    user = ( await db.execute(select(User).where(User.provider == provider, User.provider_id == provider_id))).scalars().first()

    if not user:
        user = User(username=username, email=email, password=None, provider=provider, provider_id=provider_id, is_online=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    payload = {
        'id': user.id,
        'username':user.username,
        'email': user.email 
    }

    access_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='access', exp=10)
    refresh_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='refresh', exp=1440)

    # if DEBUG:
    redirect = RedirectResponse(url=f'{FRONTEND_URL}/home')
    # else:
    #     redirect = RedirectResponse(url=f'{FRONTEND_URL_DEPLOY}/home')

    set_cookie(redirect, key='access', value=access_token)
    set_cookie(redirect, key='refresh', value=refresh_token)

    return redirect

@router.get('/refresh')
async def get_access_token(request: Request, res: Response):
    refresh = request.cookies.get('refresh')

    if not refresh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    payload = verify_token(token=refresh)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


    access_token = encode_token(payload=payload, SECRET_KEY=SECRET_KEY, algoritm=ALGORITM, type='access', exp=10)

    set_cookie(res=res, value=access_token, key='access')

    return {'message': 'Success'}


@router.delete('/logout')
async def log_out(res: Response):
    res.delete_cookie(path='/', key='access')
    res.delete_cookie(path='/', key='refresh')

    return {'message': 'Success'}