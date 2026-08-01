import sqlite3

conn = sqlite3.connect("leadflow.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(

    id INTEGER PRIMARY KEY,

    theme TEXT

)
""")

cursor.execute("""
INSERT OR IGNORE INTO settings(
    id,
    theme
)
VALUES(
    1,
    'dark'
)
""")

conn.commit()
conn.close()

print("Settings table created successfully!")