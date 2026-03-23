from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, UploadFile, File
from ...db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...models.message.message import Message, MessageType
from ...models.user.user import User
from ...services.connection_manager import manager
from ...services.token import get_current_user
from datetime import datetime
import os
import shutil

router = APIRouter()

@router.get('/{chat_id}/messages')
async def get_messages(chat_id: int, db: AsyncSession = Depends(get_db)):
    return ( await db.execute(select(Message).where(Message.chat_id == chat_id))).scalars().all()

@router.post('/{chat_id}/upload')
async def upload_file(chat_id: int, file: UploadFile = File(...)):
    folder = f'uploads/{chat_id}'
    os.makedirs(folder, exist_ok=True)

    file_path = f'{folder}/{file.filename}'

    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    return {'file_url': file_path}


@router.websocket('/ws/{chat_id}')
async def websocket_endpoint(websocket: WebSocket, chat_id: int, db: AsyncSession = Depends(get_db), ):
    await manager.connect(chat_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            message = Message(chat_id=chat_id, sender_id=data['sender_id'], content=data['content'], type=MessageType(data.get('type', 'text')), file_url=data.get('file_url'), created_at=datetime.utcnow())
            db.add(message)
            await db.commit()
            await db.refresh(message)

            await manager.broadcast(chat_id, {
                'id': message.id,
                'sender_id': message.sender_id,
                'content': message.content,
                'created_at': str(message.created_at)
            })

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)


@router.patch('/{chat_id}/message/{id}')
async def remake_message(chat_id: int, id: int, new_content: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    message = (await db.execute(select(Message).where(Message.chat_id == chat_id, Message.id == id, Message.sender_id == user.id))).scalars().first()

    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Message not found')

    message.content = new_content
    await db.commit()
    await db.refresh(message)

    return message