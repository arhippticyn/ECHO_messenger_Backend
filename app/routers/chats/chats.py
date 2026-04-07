from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ...models.chat.chat import Chat, ChatType
from ...models.chat.chatParticant import ChatParticipant, ChatParticipantType
from ...models.user.user import User
from ...db.session import get_db
from ...schemas.chats.chats import ChatCreateGroup, ChatCreatePrivate, ChatResponse
from ...services.token import get_current_user
from typing import List

router = APIRouter()

@router.post('/group')
async def create_group_chat(chat: ChatCreateGroup, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat_db = Chat(type=ChatType.group, title=chat.title)

    db.add(chat_db)
    await db.flush()


    db.add(ChatParticipant(chat_id=chat_db.id, user_id=user.id, role=ChatParticipantType.admin))

    for participant_id in chat.participants:
        db.add(ChatParticipant(chat_id=chat_db.id, user_id=participant_id, role=ChatParticipantType.base))

    await db.commit()
    await db.refresh(chat_db)

    return chat_db

@router.post('/private')
async def create_private_chat(chat: ChatCreatePrivate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat_db = Chat(type=ChatType.private, title=None)
    db.add(chat_db)
    await db.flush()

    db.add(ChatParticipant(chat_id=chat_db.id, user_id=user.id, role=ChatParticipantType.base))
    db.add(ChatParticipant(chat_id=chat_db.id, user_id=chat.user_id, role=ChatParticipantType.base))

    await db.commit()
    await db.refresh(chat_db)

    return chat_db

@router.get('', response_model=List[ChatResponse])
async def get_all_chats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chats = ( await db.execute(select(Chat)
        .join(ChatParticipant)
        .where(ChatParticipant.user_id == user.id)
        .options(selectinload(Chat.participants)))).scalars().all()

    response_data = []

    for chat in chats:
        participants_list = [
            {"id": p.id, "username": p.username, "is_online": p.is_online} 
            for p in chat.participants
        ]

        chat_dict = {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title,
            "participants": participants_list,
            "interlocutor_name": None # По умолчанию
        }

        if chat.type == ChatType.private: 
            interlocutor = next((p for p in chat.participants if p.id != user.id), None)
            if interlocutor:
                chat_dict["interlocutor_name"] = interlocutor.username
            else:
                chat_dict["interlocutor_name"] = "Saved Messages (You)"

        response_data.append(chat_dict)

    return response_data

@router.get('/{chat_id}')
async def get_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Chat).where(Chat.id == chat_id))).scalars().first()

@router.delete('/{chat_id}')
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_db)):
    chat = ( await db.execute(select(Chat).join(ChatParticipant).where(ChatParticipant.chat_id == chat_id))).scalars().first()

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Chats is not found')

    await db.delete(chat)
    await db.commit()

    return {'message': 'Success'}

@router.post('/{chat_id}/participants')
async def add_participant_to_chat(chat_id: int,user_id: int, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(
        select(ChatParticipant).where(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id
        )
    )).scalars().first()

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already in chat')
    

    particpant = ChatParticipant(chat_id=chat_id, user_id=user_id, role=ChatParticipantType.base)

    db.add(particpant)
    await db.commit()
    await db.refresh(particpant)

    return particpant

@router.delete('/{chat_id}/participants/{user_id}')
async def delete_parcitipant(chat_id: int, user_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    parcitipant = ( await db.execute(select(ChatParticipant).where(ChatParticipant.chat_id == chat_id, ChatParticipant.user_id == user_id))).scalars().first()

    admin = ( await db.execute(select(ChatParticipant).where(ChatParticipant.chat_id == chat_id, ChatParticipant.role == ChatParticipantType.admin))).scalars().first()

    if not admin or user.id != admin.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only admin can remove participants')

    await db.delete(parcitipant)
    await db.commit()

    return {'message': 'Success'}