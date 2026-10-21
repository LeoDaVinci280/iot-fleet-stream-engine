"""
Application configuration.

Centralizes all environment variables used by the project.
"""

from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    postgres_db: str = os.getenv("POSTGRES_DB", "fleetdb")

    kafka_broker: str = os.getenv(
        "KAFKA_BROKER",
        "localhost:9092"
    )

    kafka_topic: str = os.getenv(
        "KAFKA_TOPIC",
        "fleet-telemetry"
    )

    database_url: str = (
        f"postgresql+psycopg2://"
        f"{postgres_user}:{postgres_password}"
        f"@localhost:5432/{postgres_db}"
    )


settings = Settings()