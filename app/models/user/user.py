from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from ...db.base import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(250))
    password: Mapped[str] = mapped_column(nullable=True)
    provider: Mapped[str] = mapped_column()
    provider_id: Mapped[str] = mapped_column()
    is_online: Mapped[bool] = mapped_column(default=False, server_default='false')

    chats: Mapped[list['Chat']] = relationship(
    'Chat',
    secondary='chatparticipant',
    back_populates='participants'
)