from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import Student, ReadingSession
from app.models.pydantic_schemas import TeacherDashboard, TeacherDashboardStudent

router = APIRouter()

@router.get("/teacher/dashboard", response_model=TeacherDashboard)
def get_teacher_dashboard(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    dashboard_students = []
    
    for student in students:
        last_session = db.query(ReadingSession).filter(
            ReadingSession.student_id == student.id
        ).order_by(ReadingSession.created_at.desc()).first()
        
        all_sessions = db.query(ReadingSession).filter(
            ReadingSession.student_id == student.id
        ).order_by(ReadingSession.created_at.asc()).all()
        
        progress = "−"
        if len(all_sessions) >= 2:
            first_wpm = all_sessions[0].wpm
            last_wpm = all_sessions[-1].wpm
            if last_wpm > first_wpm:
                progress = "↑"
            elif last_wpm < first_wpm:
                progress = "↓"
        
        needs_attention = False
        if last_session and last_session.accuracy < 80:
            needs_attention = True
        
        dashboard_students.append(
            TeacherDashboardStudent(
                id=student.id,
                name=student.name,
                last_session_date=last_session.completed_at if last_session else None,
                wpm=float(last_session.wpm) if last_session else None,
                accuracy=float(last_session.accuracy) if last_session else None,
                progress=progress,
                needs_attention=needs_attention
            )
        )
    
    return TeacherDashboard(students=dashboard_students)
