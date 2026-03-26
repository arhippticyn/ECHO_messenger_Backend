from fastapi import FastAPI
import app.db.models
from fastapi.middleware.cors import CORSMiddleware
from .routers.router import router
from starlette.middleware.sessions import SessionMiddleware
from .core.config import SECRET_KEY, FRONTEND_URL

app = FastAPI()

origins = [
    "http://localhost:5173"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)

app.include_router(router=router)


@app.get('/')
def init():
    return {'message': 'API is working. See documentation /docs'}