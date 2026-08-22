from app.security.hash import hash_password, verify_password

password = "hello123"

hashed = hash_password(password)

print("Original Password :", password)
print("Hashed Password   :", hashed)
print("Password Match    :", verify_password(password, hashed))