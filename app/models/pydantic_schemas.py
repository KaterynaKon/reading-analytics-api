from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ErrorInput(BaseModel):
    word: str
    type: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    confidence: Optional[float] = None
    duration: Optional[float] = None
    position: Optional[int] = None

class SessionInput(BaseModel):
    student_id: int
    story_id: Optional[int] = None
    wpm: float
    accuracy: float
    total_words: int
    correct_words: int
    errors: List[ErrorInput]
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

class ErrorOutput(BaseModel):
    id: int
    word: str
    error_type: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    
    class Config:
        orm_mode = True

# ЯК МАЄ БУТИ:
class SessionOutput(BaseModel):
    id: int
    student_id: int
    story_id: Optional[int] = None
    wpm: float
    accuracy: float
    error_count: int
    created_at: Optional[datetime] = None  # <-- РЯДОК ЗМІНЕНО ТУТ
    errors: List[ErrorOutput]
    
    class Config:
        orm_mode = True

class ProgressMetrics(BaseModel):
    wpm_trend: float
    accuracy_trend: float
    total_sessions: int
    average_wpm: float
    average_accuracy: float

class FrequentError(BaseModel):
    error_type: str
    count: int

class StudentAnalytics(BaseModel):
    student_id: int
    student_name: str
    progress: ProgressMetrics
    frequent_errors: List[FrequentError]
    difficult_words: List[dict]
    last_session_date: Optional[datetime]
    last_session_audio_url: Optional[str] = None

class TeacherDashboardStudent(BaseModel):
    id: int
    name: str
    last_session_date: Optional[datetime]
    wpm: Optional[float]
    accuracy: Optional[float]
    progress: str
    needs_attention: bool

class TeacherDashboard(BaseModel):
    students: List[TeacherDashboardStudent]

class SessionOutput(BaseModel):
    id: int
    student_id: int
    story_id: Optional[int] = None
    wpm: float
    accuracy: float
    error_count: int
    created_at: datetime
    errors: List[ErrorOutput]
    audio_url: Optional[str] = None  # <-- НОВЕ ПОЛЕ
    
    class Config:
        orm_mode = True