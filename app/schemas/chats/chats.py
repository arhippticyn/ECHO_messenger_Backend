from pydantic import BaseModel

class ChatCreatePrivate(BaseModel):
    user_id: int

class ChatCreateGroup(BaseModel):
    title: str
    participants: list[int]
