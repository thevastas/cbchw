"""
Consumer service for the Cybercare package.

This module provides functionality to receive and store security events
via an HTTP API, storing them in a PostgreSQL database.
"""

import json
import logging
from typing import Any, Dict

import psycopg2
import psycopg2.extensions
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from psycopg2 import sql

from cybercare.utils import setup_basic_app

app = FastAPI()


# pylint: disable=too-few-public-methods
class PostgresEventStorage:
    """PostgreSQL implementation of event storage.

    This class provides functionality to store event data in a PostgreSQL database.
    It handles connection management and data persistence operations.

    Attributes:
        host (str): Database server hostname
        port (int): Database server port
        dbname (str): Database name
        user (str): Database username
        password (str): Database password
        table_name (str): Name of the table to store events
    """

    def __init__(self, config: Dict[str, Any]):
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 5432)
        self.dbname = config.get("name", "events_db")
        self.user = config.get("user", "postgres")
        self.password = config.get("password", "postgres")
        self.table_name = config.get("table_name", "events")
        logging.info(
            "PostgreSQL storage configured for %s:%s/%s",
            self.host,
            self.port,
            self.dbname,
        )

    def _get_connection(self) -> psycopg2.extensions.connection:
        """Create and return a new database connection.

        Returns:
            psycopg2.connection: A new connection to the PostgreSQL database
        """
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    def store_event(self, event: Dict[str, Any]) -> bool:
        """Store an event in the PostgreSQL database.

        Args:
            event (Dict[str, Any]): The event data to store

        Returns:
            bool: True if the event was stored successfully, False otherwise
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        sql.SQL(
                            "INSERT INTO {} (event_type, event_payload) VALUES (%s, %s)"
                        ).format(sql.Identifier(self.table_name)),
                        (event.get("event_type", ""), event.get("event_payload", "")),
                    )
                return True
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Error storing event: %s", e)
            return False


def validate_event(event: Dict[str, Any]) -> bool:
    """Validate that an event conforms to the required format.

    This function checks if the provided event is a dictionary with 'event_type'
    and 'event_payload' keys, both containing string values.

    Args:
        event (Dict[str, Any]): The event to validate

    Returns:
        bool: True if the event is valid, False otherwise
    """
    if not isinstance(event, dict):
        return False

    if "event_type" not in event or "event_payload" not in event:
        return False

    if not isinstance(event["event_type"], str) or not isinstance(
        event["event_payload"], str
    ):
        return False

    return True


def get_storage() -> PostgresEventStorage:
    """Dependency that provides the configured event storage.

    Returns:
        PostgresEventStorage: The configured event storage instance
    """
    return app.state.storage


storage_dependency = Depends(get_storage)


@app.post("/event")
async def receive_event(
    request: Request, storage: PostgresEventStorage = storage_dependency
) -> Dict[str, str]:
    """Handle incoming event POST requests.

    This endpoint receives events in JSON format, validates them,
    and stores them in the configured storage.

    Args:
        request (Request): The FastAPI request object
        storage (PostgresEventStorage): The event storage dependency

    Returns:
        dict: A success response if the event is stored

    Raises:
        HTTPException: 400 if the event format is invalid or not JSON
                      500 if storage fails
    """
    try:
        event = await request.json()
        logging.info("Received event: %s", event)

        if not validate_event(event):
            logging.warning("Invalid event format: %s", event)
            raise HTTPException(status_code=400, detail="Invalid event format")

        if storage.store_event(event):
            return {"status": "success", "message": "Event stored successfully"}
        raise HTTPException(status_code=500, detail="Failed to store event")
    except json.JSONDecodeError as e:
        logging.warning("Failed to decode JSON: %s", e)
        raise HTTPException(status_code=400, detail="Invalid JSON") from e


def main() -> None:
    """Run the event consumer service.

    Sets up logging, loads configuration, initializes storage,
    and starts the FastAPI server.
    """
    config = setup_basic_app("Event Consumer", "consumer")

    if not config:
        logging.error("Configuration is empty or invalid. Exiting.")
        return

    server_config = config.get("server", {})
    # Note: database config is now at the top level
    db_config = setup_basic_app("Event Consumer", "database")

    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8000)

    app.state.storage = PostgresEventStorage(db_config)

    logging.info("Starting Event Cons   umer service on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
