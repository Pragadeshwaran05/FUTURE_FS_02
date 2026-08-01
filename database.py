import sqlite3

DATABASE = "leadflow.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ------------------------
    # Admin Table
    # ------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL

    )
    """)

    # ------------------------
    # Leads Table
    # ------------------------
    # ------------------------
# Leads Table
# ------------------------
    cursor.execute("""
CREATE TABLE IF NOT EXISTS leads(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT,

    phone TEXT,

    company TEXT,

    service TEXT,

    budget TEXT,

    source TEXT,

    status TEXT DEFAULT 'New',

    message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

    # ------------------------
    # Notes Table
    # ------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        lead_id INTEGER,

        note TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (lead_id) REFERENCES leads(id)

    )
    """)

    conn.commit()
    conn.close()

    print("Database Created Successfully!")