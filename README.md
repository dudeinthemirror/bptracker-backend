NOTE: this was built almost entirely by Cline (with Claude 3.7 Sonnet). The intent was to test Cline's agentic capabilities. Conclusion: they are quite impressive! "Meesa likes!"

# BPTracker Backend

A FastAPI backend for the [BPTracker application](git@github.com:dudeinthemirror/bptracker.git) that stores blood pressure readings in a PostgreSQL database.

## Features

- Store blood pressure readings (systolic, diastolic, heart rate)
- Retrieve readings with pagination and sorting
- Delete individual readings or all readings
- PostgreSQL database for data persistence
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

The application uses PostgreSQL for data storage. You'll need to set up a PostgreSQL database and configure the connection using environment variables.

### PostgreSQL Setup

1. Install PostgreSQL if you haven't already:
   - On Ubuntu: `sudo apt install postgresql postgresql-contrib`
   - On macOS with Homebrew: `brew install postgresql`
   - On Windows: Download from [postgresql.org](https://www.postgresql.org/download/windows/)

2. Create a database for the application:
   ```sql
   CREATE DATABASE bptracker;
   ```

3. Configure environment variables:
   - Edit the `.env` file with your PostgreSQL credentials

The application will use the environment variables to connect to your PostgreSQL database when it starts.

### Starting PostgreSQL

To start a local PostgreSQL database:

```bash
# Start as a service (recommended)
brew services start postgresql@14

# Or run directly without a service
/opt/homebrew/opt/postgresql@14/bin/postgres -D /opt/homebrew/var/postgresql@14
```

If you don't have PostgreSQL installed, run `brew install postgresql@14` first.

### Migrating from SQLite to PostgreSQL

If you have existing data in the SQLite database and want to migrate it to PostgreSQL:

1. Set up your PostgreSQL database as described above
2. Make sure your `.env` file is configured correctly
3. Run the migration script:

```bash
python scripts/migrate_sqlite_to_postgres.py
```

This script will transfer all blood pressure readings from the SQLite database (`bptracker.db`) to your PostgreSQL database and update the sequence for the primary key.

If you need to manually update the sequence for the primary key (for example, if you're experiencing primary key conflicts), you can run:

```sql
SELECT setval('blood_pressure_readings_id_seq', (SELECT MAX(id) FROM blood_pressure_readings));
```
