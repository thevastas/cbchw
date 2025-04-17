#!/bin/bash
# Database initialization script for Event Consumer Service

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file in cybercare directory
if [ -f "$SCRIPT_DIR/cybercare/.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/cybercare/.env" | xargs)
    echo "Loaded environment variables from cybercare/.env"
else
    echo "Error: .env file not found in cybercare directory"
    exit 1
fi

CONFIG_FILE="$SCRIPT_DIR/cybercare/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE"
    exit 1
fi

echo "Reading database configuration from $CONFIG_FILE..."

# Manual extraction for database configuration
# This avoids complex YAML parsing
DB_HOST=$(grep -A10 "^database:" "$CONFIG_FILE" | grep "host:" | head -1 | cut -d: -f2 | tr -d ' ')
DB_PORT=$(grep -A10 "^database:" "$CONFIG_FILE" | grep "port:" | head -1 | cut -d: -f2 | tr -d ' ')
DB_NAME=$(grep -A10 "^database:" "$CONFIG_FILE" | grep "name:" | head -1 | cut -d: -f2 | tr -d ' ')
DB_USER=$(grep -A10 "^database:" "$CONFIG_FILE" | grep "user:" | head -1 | cut -d: -f2 | tr -d ' ')
DB_TABLE_NAME=$(grep -A10 "^database:" "$CONFIG_FILE" | grep "table_name:" | head -1 | cut -d: -f2 | tr -d ' ')

# Verify required parameters are present
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_NAME" ] || [ -z "$DB_USER" ]; then
    echo "Error: Missing required database configuration parameters in $CONFIG_FILE"
    echo "  Required: host, port, name, user"
    echo "  Found: host=$DB_HOST, port=$DB_PORT, name=$DB_NAME, user=$DB_USER"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD environment variable not set in .env file"
    exit 1
fi

# Set default table name if not specified
if [ -z "$DB_TABLE_NAME" ]; then
    DB_TABLE_NAME="events"
    echo "No table name specified, using default: $DB_TABLE_NAME"
fi

echo "Database configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Name: $DB_NAME"
echo "  User: $DB_USER"
echo "  Table: $DB_TABLE_NAME"

echo "Connecting to PostgreSQL at ${DB_HOST}:${DB_PORT}..."

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "SELECT 1" postgres &>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Unable to connect to PostgreSQL. Make sure it's running and credentials are correct."
    exit 1
fi

echo "Creating database $DB_NAME if it doesn't exist..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" postgres | grep -q 1 || PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME" postgres

echo "Creating events table ($DB_TABLE_NAME)..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
CREATE TABLE IF NOT EXISTS $DB_TABLE_NAME (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(255) NOT NULL,
    event_payload TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"

echo "Database initialization completed successfully."
