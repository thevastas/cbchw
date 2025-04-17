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
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection
    storage = PostgresEventStorage(mock_db_config)
    mock_connect.reset_mock()
    mock_cursor.reset_mock()
    mock_connection.reset_mock()

    event = {"event_type": "message", "event_payload": "test"}
    result = storage.store_event(event)

    mock_connect.assert_called_once()
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()

    assert result is True


@patch("psycopg2.connect")
def test_store_event_exception(mock_connect, mock_db_config):
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Database error")
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_connection
    storage = PostgresEventStorage(mock_db_config)
    mock_connect.reset_mock()
    mock_cursor.reset_mock()
    mock_connection.reset_mock()
    mock_cursor.execute.side_effect = Exception("Database error")

    event = {"event_type": "message", "event_payload": "test"}
    result = storage.store_event(event)

    mock_connect.assert_called_once()
    mock_cursor.execute.assert_called_once()
    assert result is False
