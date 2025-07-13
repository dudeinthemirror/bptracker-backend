# Blood Pressure Tracker Backend

This is a FastAPI-based backend service for tracking blood pressure readings. When analyzing this codebase:

## Key Components

1. **FastAPI Application** (`src/main.py`) - Main application entry point with CORS configuration
2. **Database Models** (`src/models.py`) - SQLAlchemy models for blood pressure readings
3. **API Schemas** (`src/schemas.py`) - Pydantic models for request/response validation
4. **Database Configuration** (`src/database.py`) - SQLite database setup and session management
5. **API Routes** (`src/routers/readings.py`) - CRUD endpoints for blood pressure readings

## Architecture Notes

- Uses SQLAlchemy ORM with SQLite database
- Implements RESTful API patterns
- Includes data validation with Pydantic
- CORS enabled for frontend integration
- Migration script available for PostgreSQL transition

## Development Guidelines

- Follow FastAPI best practices for async/await patterns
- Maintain proper error handling and HTTP status codes
- Ensure all endpoints include proper request/response models
- Keep database operations within appropriate transaction scopes