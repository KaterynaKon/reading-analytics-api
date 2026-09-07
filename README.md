# Reading Analytics API

Backend service for reading session analytics. Helps teachers track student progress, identify error patterns, and generate personalized recommendations.

## 🚀 Features

- **Session Storage** - Store reading sessions with errors (POST /api/sessions)
- **Student History** - View all sessions for a student (GET /api/students/{id}/sessions)
- **Statistics** - Average WPM, accuracy, and session count (GET /api/students/{id}/stats)
- **Analytics** - Progress trends, frequent errors, difficult words (GET /api/students/{id}/analytics)
- **Recommendations** - Personalized practice suggestions (GET /api/students/{id}/recommendations)
- **Teacher Dashboard** - Overview of all students (GET /api/teacher/dashboard)

## 🛠️ Tech Stack

- Python 3.10+
- FastAPI
- SQLAlchemy ORM
- SQLite / PostgreSQL
- Pydantic for validation
- Docker support

## 📦 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd reading-analytics-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
# or
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Set up database (SQLite by default)
# For PostgreSQL with Docker:
docker-compose up -d db

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000