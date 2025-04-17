## Project Structure

The project follows a standard Python package structure.

## Architecture

The system follows a simple architecture with clear separation of concerns:

1. **Event Propagator Service**
   - Reads events from a JSON file
   - Sends random events to the Consumer at configurable intervals
   - All sensitive configuration in environment variables

2. **Event Consumer Service**
   - Receives events via HTTP API
   - Validates event format
   - Stores events in PostgreSQL database
   - No database schema initialization in code (handled by separate script)


The project includes:
- Unit tests for the Event Propagator
- Unit tests for the Event Consumer

# Event Communication System

This project implements two services that communicate with each other: an Event Propagator that periodically sends predefined events, and an Event Consumer that receives and stores these events.

## Services Overview

### Event Propagator

The Event Propagator service periodically sends random JSON events to a specified HTTP endpoint.

Features:
- Configurable period between events (in seconds)
- Configurable HTTP endpoint for sending events
- Configurable JSON file containing the events to be sent
- Random selection of events

### Event Consumer

The Event Consumer service exposes an HTTP API endpoint that receives and stores events.

Features:
- Exposes an HTTP API endpoint at `/event` for POST requests
- Configurable port for the HTTP API
- Uses PostgreSQL database for event storage
- Validates incoming event format

## Installation

1. Clone the repository
2. Install the package and dependencies:

```bash
# Create a virtual environment and activate it
python -m venv venv && source venv/bin/activate

# Install python module in development mode
pip install -e .
```

## Environment Variables

Sensitive information is stored in a `.env` file:

```
# Database configuration
DB_PASSWORD=postgres
```

If you are running a test-setup, you can use DB_PASSWORD that is defined in the `.env` file in postgres directory:
```
DB_PASSWORD=krTa9YVz7MwYcOLCZ0QKZ3eYHlSCtsX+AvxxN7dN
```

## Database Setup
```
make setup
```

## Configuration

Configuration of the propagator, consumer and other database settings is done via `config.yaml` file

## Usage

Use `make` to get the information about usage:

```
  make help           - Show this help message
  make all            - Setup environment and run all services
  make setup          - Initialize the environment (database and schema)
  make db             - Start PostgreSQL container
  make db-stop        - Stop PostgreSQL container
  make init           - Initialize database schema
  make run-consumer   - Run only the event consumer service
  make run-propagator - Run only the event propagator service
  make run            - Run both consumer and propagator services
  make clean          - Stop services and clean up cache files

```

## Event Format

The system accepts events in the following format:

```json
{
    "event_type": "string",
    "event_payload": "string"
}
```

## Sample Events

A sample `events.json` file is provided with predefined events.

## Notes

- The Event Consumer validates that both `event_type` and `event_payload` are strings
- The Event Propagator sends events randomly from the provided events file
- PostgreSQL is used for database storage with a table for events
- YAML configuration files are used with environment variable substitution
- Sensitive information is stored in the `.env` file (not committed to version control)
- Tests are provided along with the code
