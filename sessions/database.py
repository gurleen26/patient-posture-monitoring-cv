import sqlite3, json
from datetime import datetime

def init_db():
    conn = sqlite3.connect("posturemed.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            exercise TEXT,
            status TEXT,
            angles TEXT,
            issues TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_session(exercise, analysis, angles):
    conn = sqlite3.connect("posturemed.db")
    conn.execute(
        "INSERT INTO sessions VALUES (NULL, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(), exercise,
         analysis["status"], json.dumps(angles), json.dumps(analysis["issues"]))
    )
    conn.commit()
    conn.close()