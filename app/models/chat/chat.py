from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, String
from ...db.base import Base
import enum

class ChatType(str, enum.Enum):
    group = 'group'
    private = 'private'

class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ChatType] = mapped_column(Enum(ChatType))
    title: Mapped[str | None] = mapped_column(String(60), nullable=True)
    participants: Mapped[list['User']] = relationship(
        'User',
        secondary='chatparticipant',
        back_populates='chats'
    )

