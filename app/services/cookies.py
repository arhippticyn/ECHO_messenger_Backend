from fastapi import Response

def set_cookie(res, key, value):
    return res.set_cookie(
        key=key,
        value=value,
        httponly=True,
        max_age=60 * 10,
        samesite='none',  
        secure=True,      
        path='/'
    )