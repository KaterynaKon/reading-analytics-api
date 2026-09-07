from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import ReadingSession, Student
from app.models.pydantic_schemas import SessionOutput, StudentAnalytics
from app.services.analytics import get_student_analytics
from app.services.recommendations import generate_recommendations

router = APIRouter()

@router.get("/students/{student_id}/sessions", response_model=list[SessionOutput])
def get_student_sessions(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    sessions = db.query(ReadingSession).filter(
        ReadingSession.student_id == student_id
    ).order_by(ReadingSession.created_at.desc()).all()
    
    return sessions

@router.get("/students/{student_id}/stats")
def get_student_stats(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    sessions = db.query(ReadingSession).filter(
        ReadingSession.student_id == student_id
    ).all()
    
    if not sessions:
        return {"message": "No sessions found for this student"}
    
    total_sessions = len(sessions)
    avg_wpm = sum(s.wpm for s in sessions) / total_sessions
    avg_accuracy = sum(s.accuracy for s in sessions) / total_sessions
    
    return {
        "student_id": student_id,
        "student_name": student.name,
        "total_sessions": total_sessions,
        "avg_wpm": float(avg_wpm),
        "avg_accuracy": float(avg_accuracy),
        "last_session": max(s.completed_at for s in sessions if s.completed_at)
    }

@router.get("/students/{student_id}/analytics", response_model=StudentAnalytics)
def get_student_analytics_endpoint(student_id: int, db: Session = Depends(get_db)):
    try:
        return get_student_analytics(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# НОВИЙ ЕНДПОІНТ: Рекомендації для студента
@router.get("/students/{student_id}/recommendations")
def get_student_recommendations(student_id: int, db: Session = Depends(get_db)):
    # Перевіряємо чи існує студент
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return generate_recommendations(student_id, student.name, db)