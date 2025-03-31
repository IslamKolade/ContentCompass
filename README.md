# Content Compass

Content Compass is a Django-based backend system for an AI-powered content recommendation platform. It includes features for user authentication, content management, subscription plans, and a recommendation engine. The project uses Redis for caching and as the Celery message broker, with Celery handling asynchronous tasks such as content recommendation recalculations and subscription renewals.

## Prerequisites

Ensure you have the following installed on your system:
- Python 3.12 (or a compatible version)
- Redis
- pip
- virtualenv (recommended for dependency management)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/IslamKolade/ContentCompass.git
cd ContentCompass
```

### 2. Create and Activate a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

- **For Windows:**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- **For macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies

Install all required dependencies using pip:

```bash
pip install -r requirements.txt
```

### 4. Start the Redis Server

Redis must be running for Celery to function properly. Start Redis by running:

```bash
redis-server
```

This will start Redis on `localhost` (default port `6379`).

### 5. Apply Migrations

Before running the server, apply database migrations:

```bash
python manage.py migrate
```

### 6. Start the Celery Worker

Celery workers handle background tasks. Open a new terminal and run the following:

- **For Windows (use the solo pool to avoid concurrency issues):**
  
  ```bash
  celery -A ContentCompass worker --loglevel=info --pool=solo
  ```

- **For macOS/Linux (no need for solo pool):**
  
  ```bash
  celery -A ContentCompass worker --loglevel=info
  ```

### 7. Start the Celery Beat Scheduler

Celery Beat schedules periodic tasks. Open another terminal and run:

```bash
celery -A ContentCompass beat --loglevel=info
```

### 8. Start the Django Development Server

Run the Django development server in a fourth terminal:

```bash
python manage.py runserver
```

## API Documentation

To test the API endpoints, use the provided Postman collection:
[Postman Documentation](https://www.postman.com/payload-cosmologist-68093031/content-compass/overview)

## Notes

- **Redis:** Used as a message broker for Celery and for caching.
- **Celery:** Runs in the background for processing asynchronous tasks.
- **Virtual Environment:** Recommended for dependency isolation.
- **Separate Terminals:** You must have four separate terminals running:
  1. Redis server
  2. Celery worker
  3. Celery beat scheduler
  4. Django server