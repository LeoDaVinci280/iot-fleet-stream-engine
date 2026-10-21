"""
FastAPI application.

Provides REST endpoints for telemetry and alerts.
"""

from fastapi import Depends
from fastapi import FastAPI
from sqlalchemy.orm import Session

from src.database import Alert
from src.database import Telemetry
from src.database import get_db

from src.producer import (
    create_temperature_anomaly,
    create_fuel_anomaly,
    create_overspeed_anomaly,
    create_full_incident,
    publish_event,
)


app = FastAPI(
    title="IoT Fleet Stream Engine",
    version="1.0.0"
)


@app.get("/health")
def health():
    """
    Health check endpoint.
    """

    return {"status": "ok"}


@app.get("/api/telemetry")
def get_telemetry(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve latest telemetry events.
    """

    telemetry = (
        db.query(Telemetry)
        .order_by(Telemetry.timestamp.desc())
        .limit(limit)
        .all()
    )

    return telemetry


@app.get("/api/telemetry/{vehicle_id}")
def get_vehicle_history(
    vehicle_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve telemetry history for a vehicle.
    """

    return (
        db.query(Telemetry)
        .filter(
            Telemetry.vehicle_id == vehicle_id
        )
        .order_by(
            Telemetry.timestamp.desc()
        )
        .limit(limit)
        .all()
    )
    
    
@app.get("/api/alerts")
def get_alerts(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve latest alerts.
    """

    return (
        db.query(Alert)
        .order_by(Alert.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    
@app.post("/api/inject-anomaly/temperature")
def inject_temperature_anomaly():
    """
    Inject a temperature anomaly.
    """

    event = create_temperature_anomaly()

    publish_event(event)

    return {
        "status": "published",
        "type": "temperature",
        "vehicle_id": event["vehicle_id"]
    }
    
    
@app.post("/api/inject-anomaly/fuel")
def inject_fuel_anomaly():
    """
    Inject a fuel anomaly.
    """
    event = create_fuel_anomaly()

    publish_event(event)

    return {
        "status": "published",
        "type": "fuel",
        "vehicle_id": event["vehicle_id"]
    }
    
    
@app.post("/api/inject-anomaly/overspeed")
def inject_overspeed_anomaly():
    """
    Inject an overspeed anomaly.
    """

    event = create_overspeed_anomaly()

    publish_event(event)

    return {
        "status": "published",
        "type": "overspeed",
        "vehicle_id": event["vehicle_id"]
    }


@app.post("/api/inject-anomaly/full")
def inject_full_incident():
    """
    Publish a full anomaly event.
    """

    event = create_full_incident()

    publish_event(event)

    return {
        "status": "published",
        "type": "full",
        "vehicle_id": event["vehicle_id"]
    }