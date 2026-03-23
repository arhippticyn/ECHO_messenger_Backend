from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from ...services.token import get_current_user, verify_token
from ...models.user.user import User
from ...schemas.auth.auth import UserResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...db.session import get_db
from ...services.connection_manager import manager

router = APIRouter()

@router.get('/me', response_model=UserResponse)
async def read_user(user: User = Depends(get_current_user)):
    return user

@router.websocket('/online')
async def set_isonline(websocket: WebSocket,token: str = Query(...), db: AsyncSession = Depends(get_db)):
    payload = verify_token(token)

    if payload is None:
        await websocket.close(code=1008)
        return
    
    user = (await db.execute(select(User).where(User.id == payload.get('id')))).scalars().first()

    await manager.connect(user.id, websocket)

    user.is_online = True
    await db.commit()

    try:
        while True:
            await websocket.receive_json()

    except WebSocketDisconnect:
        user.is_online = False
        await db.commit()
        manager.disconnect(user.id, websocket)