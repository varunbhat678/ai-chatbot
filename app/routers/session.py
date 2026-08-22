from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependency import get_db
from app.models.chat_session import ChatSession
from app.models.chat import Chat
from app.models.document import Document
from app.models.user import User
from app.auth.auth import get_current_user


router = APIRouter(
    prefix="/sessions",
    tags=["Chat Sessions"]
)


@router.post("/")
def create_session(
    document_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = None

    # If a document ID is provided, verify that it belongs to the user
    if document_id is not None:
        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == current_user.id
            )
            .first()
        )

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )

    # Create the chat session
    session = ChatSession(
        title="New Chat",
        user_id=current_user.id,
        document_id=document_id
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "message": "Chat session created successfully",
        "session_id": session.id,
        "document_id": session.document_id,
        "title": session.title
    }


@router.get("/")
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == current_user.id
        )
        .all()
    )

    return [
        {
            "session_id": session.id,
            "title": session.title,
            "document_id": session.document_id
        }
        for session in sessions
    ]


@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    # Delete all messages belonging to this session
    db.query(Chat).filter(
        Chat.session_id == session_id,
        Chat.user_id == current_user.id
    ).delete(synchronize_session=False)

    # Delete the session itself
    db.delete(session)
    db.commit()

    return {
        "message": "Chat session deleted successfully"
    }