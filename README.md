# JobTrack — Job Application Tracker

A full-stack web application that helps you track internship and job applications, with automated Gmail scanning to detect application-related emails.

**Live Demo:** https://job-tracker-2.netlify.app

---

## Features

- **User Authentication** — Register and login with JWT-based authentication
- **Manual Application Tracking** — Add, update, and delete job applications with status tracking (Applied, Interviewing, Offered, Rejected)
- **Gmail Integration** — Connect your Gmail account via OAuth 2.0 to automatically detect job-related emails and create/update applications
- **Background Processing** — Email scanning runs asynchronously using Celery and Redis without blocking the API
- **Analytics Dashboard** — View response rates, application counts by status, average days to response, and company breakdowns
- **Status History** — Every status change is recorded with timestamp and source (manual or email-triggered)

---

## Tech Stack

**Backend**
- FastAPI — REST API framework
- SQLAlchemy + Alembic — ORM and database migrations
- PostgreSQL — Primary database
- Celery + Redis — Background task queue for async email processing
- JWT (python-jose) — Authentication
- Gmail API (OAuth 2.0) — Email scanning

**Frontend**
- HTML, CSS, JavaScript (vanilla)
- Hosted on Netlify

**Deployment**
- Backend + Worker deployed on Railway
- PostgreSQL and Redis managed by Railway

---

## Architecture

User → Netlify (Frontend)
↓
Railway (FastAPI)
↓ ↓
PostgreSQL Redis
↓
Railway (Celery Worker)
↓
Gmail API

---

## Running Locally

**Prerequisites:** Python 3.12, PostgreSQL, Docker (for Redis)

```bash
# Clone the repo
git clone https://github.com/Tanmay130506/job-tracker.git
cd job-tracker

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
# Create .env file with:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/job_tracker
# REDIS_URL=redis://localhost:6379
# SECRET_KEY=your_secret_key

# Start Redis
docker run -d -p 6379:6379 redis

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A app.tasks worker --loglevel=info --pool=solo

# Start frontend (separate terminal)
cd frontend
python -m http.server 3000
```

---

## Gmail Integration Note

Gmail scanning uses OAuth 2.0. The app is currently in Google's testing mode — only pre-approved test users can connect their Gmail. To request access, contact [tanmay130625@gmail.com](mailto:tanmay130625@gmail.com).

---

## Project Structure

job-tracker/
├── app/
│ ├── main.py # FastAPI routes
│ ├── models.py # SQLAlchemy models
│ ├── schemas.py # Pydantic schemas
│ ├── crud.py # Application CRUD logic
│ ├── auth.py # Authentication logic
│ ├── gmail.py # Gmail API integration
│ ├── tasks.py # Celery background tasks
│ ├── analytics.py # SQL analytics queries
│ ├── celery_app.py # Celery configuration
│ ├── database.py # Database connection
│ └── config.py # Environment configuration
├── frontend/
│ ├── index.html # Login/Register page
│ ├── dashboard.html # Main dashboard
│ ├── css/ # Stylesheets
│ └── js/ # JavaScript files
├── alembic/ # Database migrations
├── Dockerfile
├── render.yaml # Railway deployment config
└── requirements.txt