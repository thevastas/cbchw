from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from cybercare.consumer import app, get_storage, validate_event

client = TestClient(app)


@pytest.mark.parametrize(
    "event,expected",
    [
        # Valid event
        ({"event_type": "message", "event_payload": "test"}, True),
        # Missing fields
        ({"event_type": "message"}, False),
        ({"event_payload": "test"}, False),
        ({}, False),
        # Wrong types
        ({"event_type": 123, "event_payload": "test"}, False),
        ({"event_type": "message", "event_payload": 123}, False),
        ({"event_type": 123, "event_payload": 456}, False),
        # Not a dict
        ("not a dict", False),
        (123, False),
        (None, False),
        # Edge cases
        ({"event_type": "", "event_payload": ""}, True),  # Empty strings are valid
        ({"event_type": "message", "event_payload": "a" * 1000}, True),  # Large payload
        ({"event_type": "alert", "event_payload": "特殊文字"}, True),  # Unicode
    ],
)
def test_validate_event(event, expected):
    """Test the event validation function with various input scenarios."""
    assert validate_event(event) is expected


@pytest.fixture
def mock_storage():
    """Fixture to provide a mock storage object."""
    mock = MagicMock()
    app.dependency_overrides[get_storage] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def failing_storage():
    """Fixture to provide a mock storage that fails to store events."""
    mock = MagicMock()
    mock.store_event.return_value = False
    app.dependency_overrides[get_storage] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def successful_storage():
    """Fixture to provide a mock storage that successfully stores events."""
    mock = MagicMock()
    mock.store_event.return_value = True
    app.dependency_overrides[get_storage] = lambda: mock
    yield mock
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "content,status_code,expected_response",
    [
        # Invalid JSON
        (b"invalid json", 400, {"detail": "Invalid JSON"}),
        # Invalid event format
        ({"invalid": "format"}, 400, {"detail": "Invalid event format"}),
    ],
)
def test_receive_event_invalid_input(
    content, status_code, expected_response, mock_storage
):
    """Test receiving events with invalid inputs."""
    if isinstance(content, bytes):
        response = client.post("/event", content=content)
    else:
        response = client.post("/event", json=content)

    assert response.status_code == status_code
    assert response.json() == expected_response


def test_receive_event_storage_error(failing_storage):
    """Test receiving an event when storage fails."""
    response = client.post(
        "/event", json={"event_type": "message", "event_payload": "test"}
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to store event"}

    # Verify the mock was called with the correct event
    failing_storage.store_event.assert_called_once()


def test_receive_event_success(successful_storage):
    """Test successfully receiving and storing an event."""
    response = client.post(
        "/event", json={"event_type": "message", "event_payload": "test"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Event stored successfully",
    }

    # Verify the mock was called with the correct event
    successful_storage.store_event.assert_called_once()
