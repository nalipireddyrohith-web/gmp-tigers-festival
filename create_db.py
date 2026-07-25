import sqlite3

conn = sqlite3.connect("festival.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS events(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tshirt_registration(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    tshirt_size TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    address TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS donations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_mode TEXT NOT NULL,
    transaction_id TEXT NOT NULL,
    donation_date TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS announcements(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS committee(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    designation TEXT NOT NULL,
    mobile TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ Database updated successfully!")
