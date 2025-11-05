# Project Title

## Overview
A minimal FastAPI backend.

## Local venv Quickstart
1. Create a virtual environment: `make venv`
2. Install dependencies: `make install`
3. Run the application: `make run`

## Make commands
- `make venv`: Creates a Python virtual environment in `.venv/`.
- `make install`: Installs runtime and development dependencies.
- `make run`: Runs the FastAPI application.

## Docker Quickstart
1. Copy `.env.example` to `.env`: `cp .env.example .env`
2. Build and run Docker containers: `docker-compose up --build`
3. Open the application in your browser: `http://localhost:8000`

## CORS Configuration
CORS (Cross-Origin Resource Sharing) can be configured in the `.env` file.

- To allow all origins, set `CORS_ALLOW_ALL=true`.
- To allow specific origins, set `CORS_ALLOW_ALL=false` and provide a comma-separated list of allowed origins in `CORS_ORIGINS`, for example: `CORS_ORIGINS=https://example.com,https://dev.local`

## Database
This project uses SQLAlchemy with an async engine. Instead of using migrations (like Alembic), it uses `Base.metadata.create_all()` on application startup to create all tables. This is suitable for development and assignments but not recommended for production environments.