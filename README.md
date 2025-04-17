## Project Structure

The project follows a standard Python package structure:

```
cybercare/
├── .env                       # Environment variables
├── .gitignore                 # Git ignore file
├── README.md                  # This file
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup script
├── db_init_script.sh          # Database initialization script
├── run_tests.sh               # Test runner script
├── cybercare/                 # Main package
│   ├── __init__.py            # Package marker
│   ├── consumer.py            # Event Consumer service
│   ├── propagator.py          # Event Propagator service
│   ├── consumer_config.yaml   # Consumer configuration
│   ├── propagator_config.yaml # Propagator configuration
│   └── events.json            # Sample events
└── tests/                     # Test package
    ├── __init__.py            # Package marker
    ├── conftest.py            # PyTest configuration
    ├── test_consumer.py       # Tests for Consumer
    ├── test_propagator.py     # Tests for Propagator
    └── test_postgres_storage.py # Tests for Storage
```## Architecture

The system follows a simple, clean architecture with clear separation of concerns:

1. **Event Propagator Service**
   - Reads events from a JSON file
   - Sends random events to the Consumer at configurable intervals
   - All sensitive configuration in environment variables

2. **Event Consumer Service**
   - Receives events via HTTP API
   - Validates event format
   - Stores events in PostgreSQL database
   - No database schema initialization in code (handled by separate script)

3. **Database Initialization Script**
   - Creates the database if it doesn't exist
   - Creates the table structure
   - Completely separate from application code## Testing

The project includes unit tests for all components. To run the tests:

```bash
# Use the test runner script
chmod +x run_tests.sh
./run_tests.sh

# Or run pytest directly
pytest -v --cov=cybercare
```

The tests include:
- Unit tests for the Event Propagator
- Unit tests for the Event Consumer
- Unit tests for the PostgreSQL storage layer
- Coverage reporting# Event Communication System

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

## Requirements

- Python 3.8+
- PostgreSQL database (running in Docker)
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository
2. Install the package and dependencies:

```bash
# Install in development mode
pip install -e .

# Or install requirements directly
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration (use the provided template as a reference)

## Environment Variables

Sensitive information is stored in a `.env` file. A template is provided in this repository - rename it to `.env` and fill in your own values:

```
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=events_db
DB_USER=postgres
DB_PASSWORD=postgres

# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Event Propagator configuration
PROPAGATOR_PERIOD=5
PROPAGATOR_ENDPOINT=http://localhost:8000/event
PROPAGATOR_EVENTS_FILE=events.json
```

## Database Setup

Before running the services, initialize the PostgreSQL database:

1. Make sure your PostgreSQL Docker container is running
2. Run the database initialization script:

```bash
chmod +x db_init_script.sh
./db_init_script.sh
```

## Configuration

Both services use YAML configuration files:

- Event Propagator: `propagator_config.yaml`
- Event Consumer: `consumer_config.yaml`

You can modify these files to adjust the settings as needed.

## Usage

### Running the Event Consumer

```bash
python event_consumer.py --config consumer_config.yaml
```

Options:
- `--config`: Path to the configuration file (default: consumer_config.yaml)

### Running the Event Propagator

```bash
python event_propagator.py --config propagator_config.yaml
```

Options:
- `--config`: Path to the configuration file (default: propagator_config.yaml)

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
- Both services use YAML configuration files with environment variable substitution
- Sensitive information is stored in the `.env` file (not committed to version control)
- Comprehensive test suite included for all components
