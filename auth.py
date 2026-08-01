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

    username = "admin"
    password = generate_password_hash("admin123")

    cursor.execute("SELECT * FROM admin WHERE username=?", (username,))

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO admin(username,password) VALUES(?,?)",
            (username, password)
        )

    conn.commit()
    conn.close()

    print("Admin account created successfully!")