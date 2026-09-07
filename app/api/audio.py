from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.schemas import ReadingSession
from app.services.storage import upload_audio
from datetime import datetime

router = APIRouter()

@router.post("/sessions/{session_id}/audio")
async def upload_session_audio(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Перевіряємо чи існує сесія
    session = db.query(ReadingSession).filter(ReadingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Завантажуємо файл в storage
    try:
        # Формуємо назву файлу: student_{id}/session_{id}_{timestamp}.webm
        file_key = f"student_{session.student_id}/session_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
        audio_url = await upload_audio(file, file_key)
        
        # Оновлюємо сесію з URL
        session.audio_url = audio_url
        db.commit()
        
        return {"audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload audio: {str(e)}")