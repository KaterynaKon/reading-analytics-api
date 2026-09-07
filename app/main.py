from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.models.database import engine, Base, get_db
from app.api import sessions, students, teacher, audio

# Створюємо таблиці
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reading Analytics API",
    description="API для аналітики читання",
    version="0.1.0"
)

# Додаємо CORS - дозволяємо запити з React та HTTP сервера
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє всі джерела (для тестування)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключаємо роутери
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(students.router, prefix="/api", tags=["students"])
app.include_router(teacher.router, prefix="/api", tags=["teacher"])
app.include_router(audio.router, prefix="/api", tags=["audio"])

@app.get("/")
def root():
    return {"message": "Reading Analytics API is running!", "status": "ok"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}