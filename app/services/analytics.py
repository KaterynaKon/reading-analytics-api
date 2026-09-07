from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.pydantic_schemas import (
    FrequentError,
    ProgressMetrics,
    StudentAnalytics,
)
from app.models.schemas import ReadingError, ReadingSession, Student


def parse_datetime(value) -> Optional[datetime]:
  """Конвертує значення з БД у datetime об'єкт."""
  if value is None:
    return None
  if isinstance(value, datetime):
    return value
  if isinstance(value, str):
    try:
      return datetime.fromisoformat(value)
    except ValueError:
      return None
  return None


def calculate_progress(sessions: List[ReadingSession]) -> ProgressMetrics:
  """Розраховує прогрес на основі всіх сесій студента."""
  if not sessions:
    return ProgressMetrics(
        wpm_trend=0,
        accuracy_trend=0,
        total_sessions=0,
        average_wpm=0,
        average_accuracy=0,
    )

  total_sessions = len(sessions)
  avg_wpm = sum(s.wpm for s in sessions) / total_sessions
  avg_accuracy = sum(s.accuracy for s in sessions) / total_sessions

  wpm_trend = 0
  accuracy_trend = 0

  if total_sessions >= 2:
    first_wpm = sessions[0].wpm
    last_wpm = sessions[-1].wpm
    first_accuracy = sessions[0].accuracy
    last_accuracy = sessions[-1].accuracy

    if first_wpm > 0:
      wpm_trend = ((last_wpm - first_wpm) / first_wpm) * 100
    if first_accuracy > 0:
      accuracy_trend = ((last_accuracy - first_accuracy) / first_accuracy) * 100

  return ProgressMetrics(
      wpm_trend=round(wpm_trend, 1),
      accuracy_trend=round(accuracy_trend, 1),
      total_sessions=total_sessions,
      average_wpm=round(float(avg_wpm), 2),
      average_accuracy=round(float(avg_accuracy), 2),
  )


def get_frequent_errors(
    db: Session, student_id: int, limit: int = 5
) -> List[FrequentError]:
  """Отримує найчастіші типи помилок студента."""
  results = (
      db.query(
          ReadingError.error_type, func.count(ReadingError.id).label('count')
      )
      .join(ReadingSession)
      .filter(ReadingSession.student_id == student_id)
      .group_by(ReadingError.error_type)
      .order_by(func.count(ReadingError.id).desc())
      .limit(limit)
      .all()
  )

  return [
      FrequentError(error_type=r[0] or 'unknown', count=r[1]) for r in results
  ]


def get_difficult_words(
    db: Session, student_id: int, limit: int = 5
) -> List[Dict]:
  """Отримує слова, які викликають найбільше труднощів."""
  results = (
      db.query(ReadingError.word, func.count(ReadingError.id).label('count'))
      .join(ReadingSession)
      .filter(ReadingSession.student_id == student_id)
      .group_by(ReadingError.word)
      .order_by(func.count(ReadingError.id).desc())
      .limit(limit)
      .all()
  )

  return [{'word': r[0], 'count': r[1]} for r in results if r[0]]


def get_student_analytics(db: Session, student_id: int) -> StudentAnalytics:
  """Збирає повну аналітику для студента."""
  student = db.query(Student).filter(Student.id == student_id).first()
  if not student:
    raise ValueError(f'Student with id {student_id} not found')

  sessions = (
      db.query(ReadingSession)
      .filter(ReadingSession.student_id == student_id)
      .order_by(ReadingSession.created_at.asc())
      .all()
  )

  progress = calculate_progress(sessions)
  frequent_errors = get_frequent_errors(db, student_id)
  difficult_words = get_difficult_words(db, student_id)

  last_session = sessions[-1] if sessions else None
  last_date = (
      parse_datetime(last_session.created_at) if last_session else None
  )

  return StudentAnalytics(
      student_id=student_id,
      student_name=student.name,
      progress=progress,
      frequent_errors=frequent_errors,
      difficult_words=difficult_words,
      last_session_date=last_date,
      last_session_audio_url=last_session.audio_url if last_session else None,
  )