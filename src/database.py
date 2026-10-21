"""
Database configuration and ORM models.
"""

from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    create_engine,
)

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from src.config import settings


engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Telemetry(Base):
    """
    Stores vehicle telemetry events.
    """

    __tablename__ = "telemetry"
    __table_args__ = (
        Index("idx_telemetry_vehicle", "vehicle_id"),
    )

    id = Column(Integer, primary_key=True)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    vehicle_id = Column(
        String(50),
        nullable=False
    )

    latitude = Column(Float)
    longitude = Column(Float)

    speed = Column(Float)

    temperature = Column(Float)

    fuel_level = Column(Float)


class Alert(Base):
    """
    Stores detected anomalies.
    """

    __tablename__ = "alerts"
    __table_args__ = (
        Index("idx_alert_vehicle", "vehicle_id"),
    )

    id = Column(Integer, primary_key=True)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    vehicle_id = Column(
        String(50),
        nullable=False
    )

    alert_type = Column(
        String(50),
        nullable=False
    )

    alert_value = Column(Float)


def create_tables() -> None:
    """
    Create database tables if they do not exist.
    """

    Base.metadata.create_all(bind=engine)
    

def get_db():
    """
    Database session dependency.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()