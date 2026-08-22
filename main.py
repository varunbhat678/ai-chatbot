from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.models.chat import Chat
from app.models.chat_session import ChatSession
from app.routers import pdf
from app.models.document import Document

from app.routers.user import router as user_router
from app.routers.chat import router as chat_router
from app.routers.session import router as session_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Chatbot API",
    description="AI Chatbot Backend API",
    version="1.0.0"
)


app.include_router(user_router)
app.include_router(chat_router)
app.include_router(session_router)
app.include_router(pdf.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI Chatbot API"
    }