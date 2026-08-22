from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="chat_sessions"
    )

    document = relationship(
        "Document",
        back_populates="chat_sessions"
    )

    chats = relationship(
        "Chat",
        back_populates="session",
        cascade="all, delete-orphan"
    )