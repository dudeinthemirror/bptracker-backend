"""SQLAlchemy ORM models."""
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

from .database import Base


class BloodPressureReading(Base):
    """SQLAlchemy model for blood pressure readings."""

    __tablename__ = "blood_pressure_readings"

    id = Column(Integer, primary_key=True, index=True)
    systolic = Column(Integer, nullable=False)
    diastolic = Column(Integer, nullable=False)
    heart_rate = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
