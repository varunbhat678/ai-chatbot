from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Welcome to AI Chatbot"
    }


@router.get("/about")
def about():
    return {
        "project": "Placement Level AI Chatbot",
        "backend": "FastAPI",
        "database": "PostgreSQL"
    }


@router.get("/health")
def health():
    return {
        "status": "Running Successfully"
    }