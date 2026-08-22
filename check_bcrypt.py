from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd.hash("hello123")
print(hashed)

print(pwd.verify("hello123", hashed))