import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from cybercare.propagator import load_events, send_event


@pytest.fixture
def event_file():
    """Fixture to create a temporary file with test events."""
    test_events = [
        {"event_type": "message", "event_payload": "test"},
        {"event_type": "user_joined", "event_payload": "TestUser"},
    ]

    temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
    json.dump(test_events, temp_file)
    temp_file.close()

    yield temp_file.name, test_events

    os.unlink(temp_file.name)


def test_load_events(event_file):
    """Test loading events from a valid JSON file."""
    file_path, expected_events = event_file
    events = load_events(file_path)

    assert len(events) == len(expected_events)
    assert events[0]["event_type"] == expected_events[0]["event_type"]
    assert events[0]["event_payload"] == expected_events[0]["event_payload"]
    assert events[1]["event_type"] == expected_events[1]["event_type"]
    assert events[1]["event_payload"] == expected_events[1]["event_payload"]


@pytest.mark.parametrize(
    "file_content,expected_result",
    [
        ("nonexistent_file.json", []),  # Nonexistent file
        ("This is not valid JSON", []),  # Invalid JSON
        ("[]", []),  # Empty array
        ("{}", {}),  # Empty object - should return empty dict, not empty list
    ],
)
def test_load_events_error_cases(file_content, expected_result):
    """Test loading events with various error cases."""
    if file_content == "nonexistent_file.json":
        # Test nonexistent file
        result = load_events(file_content)
        assert result == expected_result
    else:
        # Test invalid content
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        temp_file.write(file_content)
        temp_file.close()

        result = load_events(temp_file.name)
        assert result == expected_result

        os.unlink(temp_file.name)


@pytest.mark.parametrize(
    "status_code,response_text,expected_result",
    [
        (200, "", True),  # Success
        (299, "OK", True),  # Any 2xx status code should be successful
        (400, "Bad Request", False),  # Client error
        (500, "Internal Server Error", False),  # Server error
    ],
)
@patch("requests.post")
def test_send_event_status_codes(
    mock_post, status_code, response_text, expected_result
):
    """Test sending events with various HTTP status codes."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.text = response_text
    mock_post.return_value = mock_response

    event = {"event_type": "message", "event_payload": "test"}
    result = send_event(event, "http://test-endpoint/event")

    assert result is expected_result
    mock_post.assert_called_once_with(
        "http://test-endpoint/event", json=event, timeout=10
    )


@pytest.mark.parametrize(
    "exception,expected_result",
    [
        (Exception("Connection error"), False),
        (TimeoutError("Request timed out"), False),
        (ConnectionError("Failed to connect"), False),
    ],
)
@patch("requests.post")
def test_send_event_exceptions(mock_post, exception, expected_result):
    """Test sending events with various exceptions."""
    mock_post.side_effect = exception

    event = {"event_type": "message", "event_payload": "test"}
    result = send_event(event, "http://test-endpoint/event")

    assert result is expected_result
    mock_post.assert_called_once_with(
        "http://test-endpoint/event", json=event, timeout=10
    )


@pytest.mark.parametrize(
    "timeout_value",
    [
        1,  # Very short timeout
        5,  # Medium timeout
        30,  # Long timeout
    ],
)
@patch("requests.post")
def test_send_event_custom_timeout(mock_post, timeout_value):
    """Test sending events with various custom timeout values."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    event = {"event_type": "message", "event_payload": "test"}
    result = send_event(event, "http://test-endpoint/event", timeout=timeout_value)

    assert result is True
    mock_post.assert_called_once_with(
        "http://test-endpoint/event", json=event, timeout=timeout_value
    )


@pytest.mark.parametrize(
    "event_data",
    [
        {"event_type": "message", "event_payload": "test"},
        {"event_type": "alert", "event_payload": "security alert"},
        {"event_type": "user_joined", "event_payload": "TestUser"},
        {
            "event_type": "notification",
            "event_payload": "{'user': 'admin', 'action': 'login'}",
        },
    ],
)
@patch("requests.post")
def test_send_different_event_types(mock_post, event_data):
    """Test sending different types of events."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    result = send_event(event_data, "http://test-endpoint/event")

    assert result is True
    mock_post.assert_called_once_with(
        "http://test-endpoint/event", json=event_data, timeout=10
    )
