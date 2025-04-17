"""
Propagator service for the Cybercare package.

This module provides functionality to send simulated security events
to a consumer service at regular intervals.
"""

import json
import logging
import random
import time
from typing import Any, Dict, List

import requests

from cybercare.utils import setup_basic_app


def load_events(file_path: str) -> List[Dict[str, Any]]:
    """Load events from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing events
    Returns:
        List[Dict[str, Any]]: A list of events loaded from the file,
                             or an empty list if loading fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error("Failed to load events from %s: %s", file_path, e)
        return []


def send_event(event: Dict[str, Any], endpoint: str, timeout: int = 10) -> bool:
    """Send an event to the specified endpoint.

    Args:
        event (Dict[str, Any]): The event to send
        endpoint (str): The endpoint URL to send the event to
        timeout (int): Maximum number of seconds to wait for a response (default: 10)

    Returns:
        bool: True if the event was sent successfully, False otherwise
    """
    try:
        response = requests.post(endpoint, json=event, timeout=timeout)
        # Accept any 2xx status code as success (200-299)
        if 200 <= response.status_code < 300:
            logging.info("Successfully sent event: %s", event)
            return True
        logging.warning(
            "Failed to send event: %s, %s", response.status_code, response.text
        )
        return False
    except requests.exceptions.Timeout:
        logging.error("Timeout occurred when sending event to %s", endpoint)
        return False
    except requests.exceptions.ConnectionError:
        logging.error("Connection error when sending event to %s", endpoint)
        return False
    except Exception as e:  # pylint: disable=broad-exception-caught
        logging.error("Request error: %s", e)
        return False


def main() -> None:
    """Run the event propagator service.

    Sets up logging, loads configuration and events,
    and periodically sends events to the configured endpoint.
    """
    config = setup_basic_app("Event Propagator", "propagator")

    if not config:
        logging.error("Failed to load configuration. Exiting.")
        return

    period = config.get("period", 5)
    endpoint = config.get("endpoint", "http://localhost:8000/event")
    events_file = config.get("events_file", "events.json")

    events = load_events(events_file)
    if not events:
        logging.error("No events found. Exiting.")
        return

    logging.info("Loaded events from %s", events_file)
    logging.info("Sending events to %s every %d seconds", endpoint, period)

    try:
        while True:
            event = random.choice(events)
            send_event(event, endpoint)
            time.sleep(period)
    except KeyboardInterrupt:
        logging.info("Service stopped by user")


if __name__ == "__main__":
    main()
