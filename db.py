import sqlite3
from contextlib import contextmanager

DB_NAME = "users.db"

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                birth_date TEXT NOT NULL,
                sign TEXT NOT NULL,
                gender TEXT NOT NULL CHECK(gender IN ('m','f')),
                active INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY
            )
        """)
        conn.commit()

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def save_user(user_id, first_name, birth_date, sign, gender):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO users (user_id, first_name, birth_date, sign, gender, active)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (user_id, first_name, birth_date, sign, gender))
        conn.commit()

def get_all_active_users():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM users WHERE active = 1").fetchall()
        return [dict(row) for row in rows]

def get_user(user_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

def save_group(chat_id):
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO groups (chat_id) VALUES (?)", (chat_id,))
        conn.commit()

def get_all_groups():
    with get_connection() as conn:
        rows = conn.execute("SELECT chat_id FROM groups").fetchall()
        return [row["chat_id"] for row in rows]

def remove_group(chat_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM groups WHERE chat_id = ?", (chat_id,))
        conn.commit()
