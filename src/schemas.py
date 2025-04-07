"""Pydantic models for request/response validation."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BloodPressureReadingBase(BaseModel):
    """Base schema for blood pressure reading."""

    systolic: int = Field(..., ge=40, le=300, description="Systolic blood pressure in mmHg")
    diastolic: int = Field(..., ge=20, le=200, description="Diastolic blood pressure in mmHg")
    heart_rate: int = Field(..., ge=20, le=250, description="Heart rate in BPM")


class BloodPressureReadingCreate(BloodPressureReadingBase):
    """Schema for creating a blood pressure reading."""

    timestamp: Optional[datetime] = Field(None, description="Timestamp of the reading")


class BloodPressureReading(BloodPressureReadingBase):
    """Schema for a blood pressure reading response."""

    id: int
    timestamp: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class BloodPressureReadingList(BaseModel):
    """Schema for a list of blood pressure readings."""

    readings: List[BloodPressureReading]
