from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from ..core.config import DB_URL

engine = create_async_engine(DB_URL)

SessionLocal = async_sessionmaker(bind=engine)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
