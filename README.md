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

Docker will be added next step.