import sqlite3

conn = sqlite3.connect("leadflow.db")
cursor = conn.cursor()

# Add service column
try:
    cursor.execute("ALTER TABLE leads ADD COLUMN service TEXT")
    print("✅ service column added")
except sqlite3.OperationalError:
    print("ℹ️ service column already exists")

# Add budget column
try:
    cursor.execute("ALTER TABLE leads ADD COLUMN budget TEXT")
    print("✅ budget column added")
except sqlite3.OperationalError:
    print("ℹ️ budget column already exists")


# Create Follow-up Notes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS followups(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    lead_id INTEGER NOT NULL,

    note TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (lead_id) REFERENCES leads(id)

)
""")

print("✅ Follow-ups table created")

conn.commit()
conn.close()
print("✅ Database updated successfully!")

import sqlite3

conn = sqlite3.connect("leadflow.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_profile(
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    phone TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO admin_profile(
    id,
    full_name,
    email,
    phone
)
VALUES(
    1,
    'Administrator',
    'admin@example.com',
    '+91 XXXXX XXXXX'
)
""")

conn.commit()
conn.close()

print("admin_profile table created successfully!")