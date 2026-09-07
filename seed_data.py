import psycopg2
from datetime import datetime, timedelta

# ===== Підключення до PostgreSQL =====
conn = psycopg2.connect(
    dbname="reading_db",
    user="user",
    password="pass",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# ===== 1. Створюємо таблиці (якщо не існують) =====
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    text TEXT,
    difficulty_level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reading_sessions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    story_id INTEGER REFERENCES stories(id),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    wpm REAL,
    accuracy REAL,
    total_words INTEGER,
    correct_words INTEGER,
    error_count INTEGER,
    audio_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reading_errors (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES reading_sessions(id),
    word TEXT NOT NULL,
    position INTEGER,
    error_type TEXT,
    expected TEXT,
    actual TEXT,
    confidence REAL,
    duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# ===== 2. Очищаємо старі дані =====
cursor.execute("DELETE FROM reading_errors")
cursor.execute("DELETE FROM reading_sessions")
cursor.execute("DELETE FROM stories")
cursor.execute("DELETE FROM students")

# Скидаємо лічильники
cursor.execute("ALTER SEQUENCE students_id_seq RESTART WITH 1")
cursor.execute("ALTER SEQUENCE stories_id_seq RESTART WITH 1")
cursor.execute("ALTER SEQUENCE reading_sessions_id_seq RESTART WITH 1")
cursor.execute("ALTER SEQUENCE reading_errors_id_seq RESTART WITH 1")

# ===== 3. Додаємо студентів =====
students = [('Emma',), ('Jack',), ('Sophia',)]
cursor.executemany("INSERT INTO students (name) VALUES (%s)", students)

# ===== 4. Додаємо історії =====
stories = [
    ('The Three Little Pigs', 'Once upon a time...', 1),
    ('The Cat in the Hat', 'The sun did not shine...', 2),
]
cursor.executemany(
    "INSERT INTO stories (title, text, difficulty_level) VALUES (%s, %s, %s)",
    stories
)

# ===== 5. Отримуємо ID студентів =====
cursor.execute("SELECT id, name FROM students")
student_ids = {name: id for id, name in cursor.fetchall()}

emma_id = student_ids.get('Emma', 1)
now = datetime.now()

# ===== 6. Додаємо сесії для Emma =====
sessions_data = [
    (emma_id, 1, 64, 92, 100, 92, 2, now - timedelta(days=4)),
    (emma_id, 1, 68, 93, 100, 93, 1, now - timedelta(days=3)),
    (emma_id, 1, 71, 94, 100, 94, 1, now - timedelta(days=2)),
    (emma_id, 1, 74, 95, 100, 95, 0, now - timedelta(days=1)),
]

for student_id, story_id, wpm, accuracy, total_words, correct_words, error_count, created_at in sessions_data:
    cursor.execute("""
    INSERT INTO reading_sessions 
    (student_id, story_id, started_at, completed_at, duration_seconds, wpm, accuracy, total_words, correct_words, error_count, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        student_id,
        story_id,
        created_at,
        created_at + timedelta(minutes=2),
        120,
        wpm,
        accuracy,
        total_words,
        correct_words,
        error_count,
        created_at
    ))

# ===== 7. Отримуємо ID сесій =====
cursor.execute("SELECT id FROM reading_sessions ORDER BY id")
session_ids = [row[0] for row in cursor.fetchall()]

# ===== 8. Додаємо помилки =====
errors_data = [
    ('three', 'substitution', 'three', 'tree', 0.85),
    ('school', 'hesitation', 'school', None, 0.60),
    ('the', 'pronunciation', 'the', 'duh', 0.45),
    ('through', 'substitution', 'through', 'trough', 0.70),
]

for i, session_id in enumerate(session_ids[:3]):
    for j, (word, error_type, expected, actual, confidence) in enumerate(errors_data[:i+2]):
        cursor.execute("""
        INSERT INTO reading_errors 
        (session_id, word, position, error_type, expected, actual, confidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session_id, word, j, error_type, expected, actual, confidence))

conn.commit()
conn.close()

print("✅ Тестові дані створені в PostgreSQL!")
print("📊 Студенти: Emma, Jack, Sophia")
print("📖 Історії: The Three Little Pigs, The Cat in the Hat")
print("📈 Сесії: 4 сесії для Emma з прогресом від 64 до 74 WPM")