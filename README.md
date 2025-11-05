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

## Authentication
Authentication is handled via JWT (JSON Web Tokens).

- **Access Token**: Short-lived (15 minutes), stateless, and used for most API requests.
- **Refresh Token**: Long-lived (14 days), stored in Redis, and used to obtain a new access token.

### Token Flow
1.  **Sign up**: `POST /api/v1/auth/signup`
2.  **Log in**: `POST /api/v1/auth/login` -> returns `access_token` and `refresh_token`.
3.  **Authenticated requests**: Include `Authorization: Bearer <access_token>` in the header.
4.  **Refresh token**: `POST /api/v1/auth/refresh` with `refresh_token` in the body -> returns a new `access_token`.
5.  **Log out**: `POST /api/v1/auth/logout` with `refresh_token` in the body -> invalidates the refresh token.

### Curl Examples
**Sign up**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" -H "Content-Type: application/json" -d '{
  "fullname": "Test User",
  "email": "test@example.com",
  "password": "password123"
}'
```

**Log in**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d '{
  "email": "test@example.com",
  "password": "password123"
}'
```

**Refresh token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" -H "Content-Type: application/json" -d '{
  "refresh_token": "your_refresh_token"
}'
```

**Log out**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" -H "Content-Type: application/json" -d '{
  "refresh_token": "your_refresh_token"
}'
```
