from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import get_db
from app.models.schemas import ReadingSession, ReadingError, Student
from app.models.pydantic_schemas import SessionInput, SessionOutput

router = APIRouter()

@router.post("/sessions", response_model=SessionOutput, status_code=201)
def create_session(session_data: SessionInput, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == session_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_session = ReadingSession(
        student_id=session_data.student_id,
        story_id=session_data.story_id,
        started_at=session_data.started_at or datetime.utcnow(),
        completed_at=session_data.completed_at or datetime.utcnow(),
        duration_seconds=session_data.duration_seconds,
        wpm=session_data.wpm,
        accuracy=session_data.accuracy,
        total_words=session_data.total_words,
        correct_words=session_data.correct_words,
        error_count=len(session_data.errors)
    )
    
    db.add(db_session)
    db.flush()
    
    for error_data in session_data.errors:
        db_error = ReadingError(
            session_id=db_session.id,
            word=error_data.word,
            position=error_data.position,
            error_type=error_data.type,
            expected=error_data.expected,
            actual=error_data.actual,
            confidence=error_data.confidence,
            duration_seconds=error_data.duration
        )
        db.add(db_error)
    
    db.commit()
    db.refresh(db_session)
    
    return db_session
