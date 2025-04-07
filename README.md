NOTE: this was built almost entirely by Cline (with Claude 3.7 Sonnet). The intent was to test Cline's agentic capabilities. Conclusion: they are quite impressive! "Meesa likes!"

# BPTracker Backend

A FastAPI backend for the [BPTracker application](git@github.com:dudeinthemirror/bptracker.git) that stores blood pressure readings in a SQLite database.

## Features

- Store blood pressure readings (systolic, diastolic, heart rate)
- Retrieve readings with pagination and sorting
- Delete individual readings or all readings
- SQLite database for data persistence
- CORS support for frontend integration

## Requirements

- Python 3.8 or higher
- Dependencies listed in pyproject.toml

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd bptracker-backend
```

2. Install dependencies using uv:

```bash
uv sync
```

## Running the Server

Start the development server:

```bash
uv run fastapi dev src/main.py --host 127.0.0.1 --port 8078
```

The API will be available at http://localhost:8078

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8078/docs
- ReDoc: http://localhost:8078/redoc

## API Endpoints

- `GET /`: Root endpoint, returns status
- `GET /health`: Health check endpoint
- `GET /readings`: Get all readings with pagination
- `POST /readings`: Create a new reading
- `GET /readings/{reading_id}`: Get a specific reading
- `DELETE /readings/{reading_id}`: Delete a specific reading
- `DELETE /readings`: Delete all readings

## Database

The application uses SQLite for data storage. The database file `bptracker.db` will be created automatically in the root directory when the application starts.
