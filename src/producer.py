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

def generate_event() -> dict:
    """
    Generate a realistic telemetry event.
    """

    return {
        "vehicle_id": random.choice(VEHICLES),
        "timestamp": datetime.now(UTC).isoformat(),

        "latitude": round(
            random.uniform(43.0, 50.0),
            6
        ),

        "longitude": round(
            random.uniform(-1.0, 7.0),
            6
        ),

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


def main() -> None:
    """
    Publish telemetry continuously.
    """

    while True:

        event = generate_event()

        event = inject_anomaly(event)

        producer.produce(
            settings.kafka_topic,
            json.dumps(event).encode("utf-8")
        )

        producer.flush()

        print(
            f"Published: {event['vehicle_id']} "
            f"| speed={event['speed']} "
            f"| temp={event['temperature']}"
        )

        time.sleep(1)


if __name__ == "__main__":
    main()