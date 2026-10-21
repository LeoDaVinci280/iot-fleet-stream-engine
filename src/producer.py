"""
IoT telemetry producer.

Generates simulated fleet telemetry events and publishes
them to a Redpanda topic.
"""

import json
import random
import time
from datetime import datetime, UTC

from confluent_kafka import Producer

from src.config import settings


producer = Producer(
    {
        "bootstrap.servers": settings.kafka_broker
    }
)

VEHICLE_COUNT = 50

VEHICLES = [
    f"TRUCK-{i:03d}"
    for i in range(1, VEHICLE_COUNT + 1)
]

LOGISTICS_HUBS = [
    ("Paris", 48.8566, 2.3522),
    ("Lille", 50.6292, 3.0573),
    ("Lyon", 45.7640, 4.8357),
    ("Marseille", 43.2965, 5.3698),
    ("Bordeaux", 44.8378, -0.5792),
    ("Toulouse", 43.6047, 1.4442),
    ("Nantes", 47.2184, -1.5536),
    ("Strasbourg", 48.5734, 7.7521),
]

def generate_event() -> dict:
    """
    Generate a realistic telemetry event.
    """
    
    city, hub_lat, hub_lon = random.choice(LOGISTICS_HUBS)

    latitude = round(
        hub_lat + random.uniform(-0.25, 0.25),
        6
    )

    longitude = round(
        hub_lon + random.uniform(-0.25, 0.25),
        6
    )

    return {
        "vehicle_id": random.choice(VEHICLES),
        "timestamp": datetime.now(UTC).isoformat(),

        "latitude": latitude,

        "longitude": longitude,

        "speed": round(
            random.uniform(0, 130),
            1
        ),

        "temperature": round(
            random.uniform(2, 8),
            1
        ),

        "fuel_level": round(
            random.uniform(10, 100),
            1
        )
    }
    
def inject_anomaly(event: dict) -> dict:
    """
    Randomly inject anomalies into telemetry events.
    """

    chance = random.randint(1, 25)

    if chance == 1:
        event["temperature"] = random.uniform(10, 15)

    elif chance == 2:
        event["fuel_level"] = random.uniform(1, 5)

    elif chance == 3:
        event["speed"] = random.uniform(140, 180)

    return event


def publish_event(event: dict) -> None:
    """
    Publish a telemetry event to Redpanda.
    """

    producer.produce(
        settings.kafka_topic,
        json.dumps(event).encode("utf-8")
    )

    producer.flush()
    
    
def create_anomaly_event() -> dict:
    """
    Create a guaranteed anomalous event.
    """

    vehicle_id = random.choice(VEHICLES)

    return {
        "vehicle_id": vehicle_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "latitude": 48.8566,
        "longitude": 2.3522,
        "speed": 160.0,
        "temperature": 14.0,
        "fuel_level": 5.0
    }



def main() -> None:
    """
    Publish telemetry continuously.
    """

    while True:

        event = generate_event()

        event = inject_anomaly(event)

        publish_event(event)

        print(
            f"Published: {event['vehicle_id']} "
            f"| speed={event['speed']} "
            f"| temp={event['temperature']}"
        )

        time.sleep(1)


if __name__ == "__main__":
    main()