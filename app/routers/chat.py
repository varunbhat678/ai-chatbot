from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest
from app.services.gemini_service import generate_response
from app.services.rag_service import generate_pdf_response

from app.database.dependency import get_db
from app.models.chat import Chat
from app.models.chat_session import ChatSession
from app.models.document import Document
from app.models.user import User
from app.security.authentication import get_current_user


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.get("/")
def home():
    return {
        "message": "Chat API Working"
    }


@router.post("/send")
def send_message(
    chat: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find the session belonging to the current user
    chat_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == chat.session_id,
            ChatSession.user_id == current_user.id
        )
        .first()
    )

    if not chat_session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found"
        )

    # Get the document attached to this chat session
    document = None

    if chat_session.document_id:
        document = (
            db.query(Document)
            .filter(
                Document.id == chat_session.document_id,
                Document.user_id == current_user.id
            )
            .first()
        )

    # Get previous messages from this session
    previous_chats = (
        db.query(Chat)
        .filter(
            Chat.user_id == current_user.id,
            Chat.session_id == chat.session_id
        )
        .order_by(Chat.id.asc())
        .all()
    )

    # Build conversation history
    conversation_history = ""

    for previous_chat in previous_chats:
        conversation_history += (
            f"User: {previous_chat.message}\n"
            f"Assistant: {previous_chat.response}\n\n"
        )

    # If the session has a document, use RAG
    if document:
        ai_response = generate_pdf_response(
            chat.message,
            document.vector_path,
            document.chunks_path
        )

    # Otherwise, use normal AI chat with conversation history
    else:
        prompt = f"""
You are an AI assistant having a continuous conversation with the user.

Use the previous conversation to understand references such as
"it", "that", "this", "explain more", and follow-up questions.

Previous conversation:
{conversation_history}

Current user message:
{chat.message}

Answer the current user message naturally and accurately.
"""

        ai_response = generate_response(prompt)

    # Save the conversation
    new_chat = Chat(
        user_id=current_user.id,
        session_id=chat.session_id,
        message=chat.message,
        response=ai_response
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return {
        "session_id": chat.session_id,
        "message": chat.message,
        "response": ai_response
    }


@router.get("/history/{session_id}")
def chat_history(
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

    chats = (
        db.query(Chat)
        .filter(
            Chat.user_id == current_user.id,
            Chat.session_id == session_id
        )
        .order_by(Chat.id.asc())
        .all()
    )

    return {
        "session_id": session_id,
        "history": [
            {
                "id": chat.id,
                "message": chat.message,
                "response": chat.response
            }
            for chat in chats
        ]
    }

