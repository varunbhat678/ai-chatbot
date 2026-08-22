from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    message = Column(String, nullable=False)

    response = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    session_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="chats"
    )

    session = relationship(
        "ChatSession",
        back_populates="chats"
    )