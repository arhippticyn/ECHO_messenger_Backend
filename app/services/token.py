import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.core.config import SECRET_KEY, ALGORITM

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