import sqlite3

conn = sqlite3.connect('reading.db')
cursor = conn.cursor()

print("=== STUDENTS ===")
for row in cursor.execute("SELECT * FROM students").fetchall():
    print(row)

print("\n=== SESSIONS ===")
for row in cursor.execute("SELECT id, student_id, wpm, accuracy, created_at FROM reading_sessions").fetchall():
    print(row)

print("\n=== ERRORS ===")
for row in cursor.execute("SELECT id, session_id, word, error_type FROM reading_errors").fetchall():
    print(row)

conn.close()