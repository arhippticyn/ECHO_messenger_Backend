from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.router import router

app = FastAPI()

app.include_router(router=router)


@app.get('/')
def init():
    return {'message': 'API is working. See documentation /docs'}