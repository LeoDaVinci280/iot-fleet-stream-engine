"""
Telemetry consumer.

Consumes fleet telemetry events from Redpanda,
stores them in TimescaleDB and generates alerts.
"""

import json
from datetime import datetime, UTC

from confluent_kafka import Consumer

from src.config import settings
from src.database import Alert, SessionLocal, Telemetry

import requests

consumer = Consumer(
    {
        "bootstrap.servers": settings.kafka_broker,
        "group.id": "fleet-consumer-group",
        "auto.offset.reset": "earliest",
    }
)

consumer.subscribe([settings.kafka_topic])


def broadcast_alert(
    vehicle_id: str,
    alert_type: str,
    alert_value: float
) -> None:
    print("BROADCAST FUNCTION CALLED")
    print(
        f"BROADCASTING {alert_type} "
        f"for {vehicle_id}"
    )

    try:

        response = requests.post(
            "http://127.0.0.1:8000/api/alerts/broadcast",
            json={
                "vehicle_id": vehicle_id,
                "alert_type": alert_type,
                "alert_value": alert_value,
            },
            timeout=2,
        )

        print(response.status_code)
        print(response.text)

    except Exception as exc:

        print(
            f"WebSocket broadcast failed: {exc}"
        )


def detect_anomalies(session, event: dict) -> None:
    """
    Detect telemetry anomalies and create alerts.
    """
    print("DETECT ANOMALIES CALLED")
    alerts = []

    if event["temperature"] > 8:
        alerts.append(
            ("HIGH_TEMPERATURE", event["temperature"])
        )

    if event["fuel_level"] < 15:
        alerts.append(
            ("LOW_FUEL", event["fuel_level"])
        )

    if event["speed"] > 130:
        alerts.append(
            ("OVERSPEED", event["speed"])
        )

    for alert_type, value in alerts:

        session.add(
            Alert(
                vehicle_id=event["vehicle_id"],
                alert_type=alert_type,
                alert_value=value,
            )
        )
        
        broadcast_alert(
            vehicle_id=event["vehicle_id"],
            alert_type=alert_type,
            alert_value=value,
        )

        print(
            f"ALERT | {event['vehicle_id']} | "
            f"{alert_type} | {value}"
        )
        
        
def process_event(event: dict) -> None:
    """
    Persist telemetry data and detect anomalies.
    """

    session = SessionLocal()

    try:

        telemetry = Telemetry(
            timestamp=datetime.fromisoformat(
                event["timestamp"]
            ),
            vehicle_id=event["vehicle_id"],
            latitude=event["latitude"],
            longitude=event["longitude"],
            speed=event["speed"],
            temperature=event["temperature"],
            fuel_level=event["fuel_level"],
        )

        session.add(telemetry)

        detect_anomalies(session, event)

        session.commit()

    finally:
        session.close()
        
def main() -> None:
    """
    Start telemetry consumer.
    """

    print("Consumer started.")

    while True:

        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(msg.error())
            continue

        event = json.loads(
            msg.value().decode("utf-8")
        )

        process_event(event)

        print(
            f"Processed {event['vehicle_id']}"
        )


if __name__ == "__main__":
    main()
