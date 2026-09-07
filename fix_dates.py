import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('reading.db')
cursor = conn.cursor()

now = datetime.now()
sessions = cursor.execute("SELECT id FROM reading_sessions ORDER BY id").fetchall()

for i, (session_id,) in enumerate(sessions):
    created_at = now - timedelta(days=len(sessions) - i)
    cursor.execute(
        "UPDATE reading_sessions SET created_at = ? WHERE id = ?",
        (created_at.isoformat(), session_id)
    )

conn.commit()
conn.close()
print("✅ created_at оновлено!")