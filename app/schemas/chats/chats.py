from pydantic import BaseModel
from typing import List, Optional
from ..auth.auth import UserResponse

class ChatCreatePrivate(BaseModel):
    user_id: int

class ChatCreateGroup(BaseModel):
    title: str
    participants: list[int]


class ChatResponse(BaseModel):
    id: int
    type: str
    title: Optional[str]
    interlocutor_name: Optional[str] = None
    participants: List[UserResponse]

    class Config:
        from_attributes = True