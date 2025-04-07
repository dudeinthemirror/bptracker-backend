"""API endpoints for blood pressure readings."""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/readings",
    tags=["readings"],
)


@router.get("/", response_model=schemas.BloodPressureReadingList)
def get_readings(
    skip: int = Query(0, ge=0, description="Number of readings to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of readings to return"),
    db: Session = Depends(get_db),
):
    """
    Get all blood pressure readings.
    
    Args:
        skip: Number of readings to skip
        limit: Maximum number of readings to return
        db: Database session
        
    Returns:
        List of blood pressure readings
    """
    readings = db.query(models.BloodPressureReading).order_by(
        models.BloodPressureReading.timestamp.desc()
    ).offset(skip).limit(limit).all()
    
    return {"readings": readings}


@router.post("/", response_model=schemas.BloodPressureReading, status_code=201)
def create_reading(
    reading: schemas.BloodPressureReadingCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new blood pressure reading.
    
    Args:
        reading: Blood pressure reading data
        db: Database session
        
    Returns:
        Created blood pressure reading
    """
    db_reading = models.BloodPressureReading(
        systolic=reading.systolic,
        diastolic=reading.diastolic,
        heart_rate=reading.heart_rate,
        timestamp=reading.timestamp or datetime.now(),
    )
    
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    return db_reading


@router.get("/{reading_id}", response_model=schemas.BloodPressureReading)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific blood pressure reading by ID.
    
    Args:
        reading_id: ID of the reading to get
        db: Database session
        
    Returns:
        Blood pressure reading
        
    Raises:
        HTTPException: If reading not found
    """
    reading = db.query(models.BloodPressureReading).filter(
        models.BloodPressureReading.id == reading_id
    ).first()
    
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    
    return reading


@router.delete("/{reading_id}", status_code=204)
def delete_reading(
    reading_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a specific blood pressure reading by ID.
    
    Args:
        reading_id: ID of the reading to delete
        db: Database session
        
    Raises:
        HTTPException: If reading not found
    """
    reading = db.query(models.BloodPressureReading).filter(
        models.BloodPressureReading.id == reading_id
    ).first()
    
    if reading is None:
        raise HTTPException(status_code=404, detail="Reading not found")
    
    db.delete(reading)
    db.commit()


@router.delete("/", status_code=204)
def delete_all_readings(
    db: Session = Depends(get_db),
):
    """
    Delete all blood pressure readings.
    
    Args:
        db: Database session
    """
    db.query(models.BloodPressureReading).delete()
    db.commit()
