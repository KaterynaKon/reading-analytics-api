from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("ReadingSession", back_populates="student", cascade="all, delete-orphan")

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    text = Column(Text)
    difficulty_level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    sessions = relationship("ReadingSession", back_populates="story")

class ReadingSession(Base):
    __tablename__ = "reading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=True)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)
    
    wpm = Column(DECIMAL(5, 2))
    accuracy = Column(DECIMAL(5, 2))
    total_words = Column(Integer)
    correct_words = Column(Integer)
    error_count = Column(Integer)
    audio_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="sessions")
    story = relationship("Story", back_populates="sessions")
    errors = relationship("ReadingError", back_populates="session", cascade="all, delete-orphan")

class ReadingError(Base):
    __tablename__ = "reading_errors"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("reading_sessions.id"), nullable=False)
    
    word = Column(String, nullable=False)
    position = Column(Integer)
    error_type = Column(String)
    expected = Column(String)
    actual = Column(String)
    confidence = Column(DECIMAL(3, 2))
    duration_seconds = Column(DECIMAL(5, 2))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ReadingSession", back_populates="errors")
