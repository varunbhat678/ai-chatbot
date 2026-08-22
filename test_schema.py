from app.schemas.user import UserCreate

user = UserCreate(
    username="Varun",
    email="varun@gmail.com",
    password="12345678"
)

print(user)