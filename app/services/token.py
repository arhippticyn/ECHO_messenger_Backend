import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.core.config import SECRET_KEY, ALGORITM
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request, HTTPException, status
from ..db.session import get_db
from ..models.user.user import User
from sqlalchemy import select


def encode_token(payload: dict, SECRET_KEY: str, algoritm: str, type: str, exp: int):
    payload_copy = payload.copy()

    payload_copy['type'] = type
    payload_copy['exp'] = int((datetime.now(timezone.utc) + timedelta(minutes=exp)).timestamp())

    return jwt.encode(payload_copy, key=SECRET_KEY, algorithm=algoritm)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITM])

        return payload
    
    except InvalidTokenError:
        return None
    

async def get_current_user(request: Request,db: AsyncSession = Depends(get_db)):
    creditials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},)
    token = request.cookies.get('access')
    try:
        id = verify_token(token).get('id')

        if id is None:
            raise creditials_exception
        
    except InvalidTokenError:
        raise creditials_exception
    
    user = (await db.execute(select(User).where(User.id == id))).scalars().first()

    if user is None:
        raise creditials_exception
    
    return user