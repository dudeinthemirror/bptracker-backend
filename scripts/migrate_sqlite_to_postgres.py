#!/usr/bin/env python
"""
Migration script to transfer data from SQLite to PostgreSQL.

This script reads all blood pressure readings from the SQLite database
and inserts them into the PostgreSQL database.
"""
import os
import sys
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import SQLAlchemy models and database connection
from src.models import BloodPressureReading
from src.database import SessionLocal, engine, Base

# Load environment variables
load_dotenv()

# Path to SQLite database
SQLITE_DB_PATH = "bptracker.db"


def migrate_data():
    """Migrate data from SQLite to PostgreSQL."""
    # Check if SQLite database exists
    if not os.path.exists(SQLITE_DB_PATH):
        print(f"SQLite database not found at {SQLITE_DB_PATH}")
        return

    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Create tables in PostgreSQL if they don't exist
    Base.metadata.create_all(bind=engine)

    # Get a session for PostgreSQL
    db = SessionLocal()

    try:
        # Get all readings from SQLite
        sqlite_cursor.execute("SELECT * FROM blood_pressure_readings")
        readings = sqlite_cursor.fetchall()

        print(f"Found {len(readings)} readings in SQLite database")

        # Insert readings into PostgreSQL
        for reading in readings:
            # Convert SQLite row to dict
            reading_dict = dict(reading)
            
            # Create new reading object
            new_reading = BloodPressureReading(
                id=reading_dict["id"],
                systolic=reading_dict["systolic"],
                diastolic=reading_dict["diastolic"],
                heart_rate=reading_dict["heart_rate"],
                timestamp=datetime.fromisoformat(reading_dict["timestamp"]),
                note=reading_dict["note"]
            )
            
            # Add to session
            db.add(new_reading)
        
        # Commit all changes
        db.commit()
        
        # Update the sequence to start after the highest ID
        db.execute(
            "SELECT setval('blood_pressure_readings_id_seq', (SELECT MAX(id) FROM blood_pressure_readings))"
        )
        db.commit()
        
        print(f"Successfully migrated {len(readings)} readings to PostgreSQL")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        # Close connections
        db.close()
        sqlite_conn.close()


if __name__ == "__main__":
    print("Starting migration from SQLite to PostgreSQL...")
    migrate_data()
    print("Migration complete")
