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
- Unit tests for the PostgreSQL storage layer

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

## Requirements

- Python 3.8+
- PostgreSQL database

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
DB_PASSWORD=postgres
```

## Database Setup

Before running the services, initialize the PostgreSQL database:

1. An example docker container for the PostgreSQL server is given in `postgres` directory
2. Make sure your PostgreSQL server is running
3. Run the database initialization script:

```bash
chmod +x db_init_script.sh
./db_init_script.sh
```

## Configuration

Configuration of the propagator, consumer and other database settings is done via `config.yaml` file

## Usage

### Running the Event Consumer

```bash
python event_consumer.py
```

### Running the Event Propagator

```bash
python event_propagator.py
```

### Running the whole suite using a dockerized postgres database
```bash
make
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
