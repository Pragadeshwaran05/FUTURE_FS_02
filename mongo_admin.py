from werkzeug.security import generate_password_hash
from mongodb import admin_collection

username = "admin"

password = generate_password_hash("admin123")

if admin_collection.find_one({"username": username}) is None:
    admin_collection.insert_one({
        "username": username,
        "password": password
    })
    print("Admin Created")
else:
    print("Admin Already Exists")