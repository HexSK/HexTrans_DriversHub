from werkzeug.security import generate_password_hash
import json

x = input("Vložte heslo: ")

y = generate_password_hash(x, method="pbkdf2:sha256")
print(y)
