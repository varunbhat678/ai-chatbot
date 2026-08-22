from sqlalchemy.orm import Session
from app.models.chat import Chat


def save_chat(db: Session, user_id: int, question: str, answer: str):
    chat = Chat(
        user_id=user_id,
        question=question,
        answer=answer
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat