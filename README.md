# Audteye Live Coding — Starter

This is the starter repository for your live coding interview with Audteye.
The full problem statement will be shared at the start of the session.

## What's included

- A Django project skeleton with one app (`jobs`)
- Celery configured with Redis as broker and result backend
- A mocked external image generation provider in `jobs/providers.py`
  (this simulates a real-world flaky API — **do not modify it**)
- Postgres and Redis configured to run via Docker Compose
- Empty stubs for the model, views, and Celery task you'll implement

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Git

## Setup (~5 minutes)

1. **Start Postgres and Redis**
   ```bash
   docker compose up -d
   ```
   Verify with `docker compose ps` — both services should show `healthy`.

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   # venv\Scripts\activate     # Windows PowerShell
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the Django dev server** (in one terminal)
   ```bash
   python manage.py runserver
   ```

7. **Start the Celery worker** (in a second terminal, with venv activated)
   ```bash
   celery -A config worker -l info
   ```

## Verify the setup

In a third terminal:

```bash
curl http://localhost:8000/api/health/
```

You should see `{"ok": true}`.

The Celery worker log should show `celery@<hostname> ready.`

## What you'll do during the interview

The problem statement will be shared at the start of the session. You'll implement code in `jobs/models.py`, `jobs/views.py`, and `jobs/tasks.py`. The provider in `jobs/providers.py` should be treated as a black box — do not modify its behavior.

## If something doesn't work

Email basheer@audteye.com. We will not spend interview time on environment troubleshooting.
