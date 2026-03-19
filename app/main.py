from fastapi import FastAPI
import app.db.models
from fastapi.middleware.cors import CORSMiddleware
from .routers.router import router
from starlette.middleware.sessions import SessionMiddleware
from .core.config import SECRET_KEY

app = FastAPI()

app.include_router(router=router)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)


@app.get('/')
def init():
    return {'message': 'API is working. See documentation /docs'}