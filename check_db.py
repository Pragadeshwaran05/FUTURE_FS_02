import sqlite3

conn = sqlite3.connect("leadflow.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(leads)")

columns = cursor.fetchall()

for column in columns:
    print(column)

conn.close()