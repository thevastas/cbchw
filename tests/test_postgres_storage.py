from unittest.mock import MagicMock, patch

import pytest

from cybercare.consumer import PostgresEventStorage


@pytest.fixture
def mock_db_config():
    return {
        "host": "test_host",
        "port": 5432,
        "name": "test_db",
        "user": "test_user",
        "password": "test_password",
        "table_name": "test_events",
    }


@patch("psycopg2.connect")
def test_postgres_storage_initialization(mock_connect, mock_db_config):
    storage = PostgresEventStorage(mock_db_config)
    mock_connect.assert_not_called()

    assert storage.host == mock_db_config["host"]
    assert storage.port == mock_db_config["port"]
    assert storage.dbname == mock_db_config["name"]
    assert storage.user == mock_db_config["user"]
    assert storage.password == mock_db_config["password"]
    assert storage.table_name == mock_db_config["table_name"]


@patch("psycopg2.connect")
def test_store_event_success(mock_connect, mock_db_config):
    # Mock cursor and connection
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    # Create storage
    storage = PostgresEventStorage(mock_db_config)

    # Reset mock calls from initialization
    mock_connect.reset_mock()
    mock_cursor.reset_mock()
    mock_connection.reset_mock()

    # Test storing an event
    event = {"event_type": "message", "event_payload": "test"}
    result = storage.store_event(event)

    # Verify connection was created
    mock_connect.assert_called_once()

    # Verify SQL execution
    mock_cursor.execute.assert_called_once()

    # Verify commit and close
    mock_connection.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()

    # Verify result
    assert result is True


@patch("psycopg2.connect")
def test_store_event_exception(mock_connect, mock_db_config):
    # Mock connection to raise exception during execution
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Database error")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection

    # Create storage
    storage = PostgresEventStorage(mock_db_config)

    # Reset mock calls from initialization
    mock_connect.reset_mock()
    mock_cursor.reset_mock()
    mock_connection.reset_mock()
    mock_cursor.execute.side_effect = Exception("Database error")

    # Test storing an event that raises an exception
    event = {"event_type": "message", "event_payload": "test"}
    result = storage.store_event(event)

    # Verify connection was created
    mock_connect.assert_called_once()

    # Verify SQL execution was attempted
    mock_cursor.execute.assert_called_once()

    # Verify result indicates failure
    assert result is False
