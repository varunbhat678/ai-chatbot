from app.database.database import Base, engine

from app.models.user import User
from app.models.chat import Chat

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")