from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from ...db.base import Base
import enum

class ChatParticipantType(str, enum.Enum):
    admin = 'admin'
    base = 'base'

class ChatParticipant(Base):
    __tablename__ = 'chatparticipant'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chats.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    role: Mapped[ChatParticipantType] = mapped_column(Enum(ChatParticipantType))
    joined_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
