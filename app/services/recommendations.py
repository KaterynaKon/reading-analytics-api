from sqlalchemy.orm import Session
from app.models.schemas import ReadingSession, ReadingError
from app.services.analytics import get_frequent_errors, get_difficult_words
from typing import List, Dict
import re


def get_phonetic_patterns(words: List[str]) -> List[str]:
    """Визначає фонетичні патерни на основі слів"""
    patterns = []
    
    # Перевіряємо наявність звуку "th"
    th_words = [w for w in words if re.search(r'th', w, re.IGNORECASE)]
    if th_words:
        patterns.append("th_sound")
    
    # Перевіряємо довгі слова (складні для читання)
    long_words = [w for w in words if len(w) > 6]
    if long_words:
        patterns.append("long_words")
    
    # Перевіряємо слова з "sh", "ch", "wh"
    digraph_words = [w for w in words if re.search(r'(sh|ch|wh)', w, re.IGNORECASE)]
    if digraph_words:
        patterns.append("digraphs")
    
    return patterns


def generate_recommendations(student_id: int, student_name: str, db: Session) -> Dict:
    """Генерує рекомендації на основі аналітики студента"""
    
    # Отримуємо дані для аналізу
    difficult_words_data = get_difficult_words(db, student_id, limit=10)
    frequent_errors_data = get_frequent_errors(db, student_id)
    
    difficult_words = [item["word"] for item in difficult_words_data]
    error_types = {item.error_type: item.count for item in frequent_errors_data}
    
    recommendations = []
    practice_words = []
    next_difficulty = "medium"
    
    # ---- АНАЛІЗ ФОНЕТИЧНИХ ПАТЕРНІВ ----
    if difficult_words:
        patterns = get_phonetic_patterns(difficult_words)
        
        if "th_sound" in patterns:
            recommendations.append(
                "Practice words with 'th' sound: " + 
                ", ".join([w for w in difficult_words if 'th' in w.lower()])
            )
            practice_words.extend([w for w in difficult_words if 'th' in w.lower()])
        
        if "digraphs" in patterns:
            digraph_words = [w for w in difficult_words if re.search(r'(sh|ch|wh)', w, re.IGNORECASE)]
            recommendations.append(
                "Practice digraphs (sh, ch, wh): " + ", ".join(digraph_words)
            )
            practice_words.extend(digraph_words)
        
        if "long_words" in patterns:
            long_words = [w for w in difficult_words if len(w) > 6]
            recommendations.append(
                "Break down long words into syllables: " + ", ".join(long_words)
            )
            practice_words.extend(long_words)
    
    # ---- АНАЛІЗ ТИПІВ ПОМИЛОК ----
    if error_types.get("substitution", 0) > 5:
        recommendations.append(
            "Work on substitution errors - focus on word endings and visual similarity"
        )
    
    if error_types.get("hesitation", 0) > 5:
        recommendations.append(
            "Practice reading aloud to reduce hesitation and build fluency"
        )
    
    if error_types.get("pronunciation", 0) > 3:
        recommendations.append(
            "Listen to correct pronunciation and repeat words multiple times"
        )
    
    # ---- РЕКОМЕНДАЦІЯ РІВНЯ СКЛАДНОСТІ ----
    total_errors = sum(error_types.values()) if error_types else 0
    
    if total_errors > 15:
        next_difficulty = "easy"
        recommendations.append("Start with easier stories to build confidence")
    elif total_errors > 8:
        next_difficulty = "medium"
        recommendations.append("Continue with medium difficulty stories")
    else:
        next_difficulty = "advanced"
        recommendations.append("Ready for more advanced stories!")

    # ---- ЗАГАЛЬНА РЕКОМЕНДАЦІЯ ----
    if not recommendations:
        recommendations.append("Great progress! Continue reading regularly.")
    
    # Унікальні слова для практики (без дублікатів)
    unique_practice_words = list(dict.fromkeys(practice_words))
    
    return {
        "student_id": student_id,
        "student_name": student_name,
        "recommendations": recommendations,
        "practice_words": unique_practice_words[:5],  # Топ 5 слів для практики
        "next_story_difficulty": next_difficulty
    }