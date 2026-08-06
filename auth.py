import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "leadflow.db"

def create_admin():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    import os

    username = os.getenv("ADMIN_USERNAME", "admin")
    raw_password = os.getenv("ADMIN_PASSWORD", "admin123")
    password = generate_password_hash(raw_password)

    cursor.execute("SELECT * FROM admin WHERE username=?", (username,))

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO admin(username,password) VALUES(?,?)",
            (username, password)
        )

    conn.commit()
    conn.close()

    print("Admin account created successfully!")