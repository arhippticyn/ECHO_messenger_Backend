from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from ..core.config import DB_URL, DEBUG

clean_url = DB_URL.split("?")[0] if DB_URL else DB_URL

if DEBUG:
    engine = create_async_engine(DB_URL)
else:
    engine = create_async_engine(
        clean_url, 
        echo=True,
        connect_args={"ssl": "require"}
    )

SessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession, expire_on_commit=False)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
