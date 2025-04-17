from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from cybercare.consumer import app, get_storage, validate_event

client = TestClient(app)


def test_validate_event_valid():
    event = {"event_type": "message", "event_payload": "test"}
    assert validate_event(event) is True


def test_validate_event_missing_fields():
    event1 = {"event_type": "message"}
    event2 = {"event_payload": "test"}
    event3 = {}

    assert validate_event(event1) is False
    assert validate_event(event2) is False
    assert validate_event(event3) is False


def test_validate_event_wrong_type():
    event1 = {"event_type": 123, "event_payload": "test"}
    event2 = {"event_type": "message", "event_payload": 123}
    event3 = {"event_type": 123, "event_payload": 456}

    assert validate_event(event1) is False
    assert validate_event(event2) is False
    assert validate_event(event3) is False


def test_validate_event_not_dict():
    assert validate_event("not a dict") is False
    assert validate_event(123) is False
    assert validate_event(None) is False


def override_get_storage():
    mock_storage = MagicMock()
    return mock_storage


@pytest.mark.asyncio
async def test_receive_event_invalid_json():
    app.dependency_overrides[get_storage] = override_get_storage

    response = client.post("/event", content=b"invalid json")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_receive_event_invalid_format():
    app.dependency_overrides[get_storage] = override_get_storage

    response = client.post("/event", json={"invalid": "format"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid event format"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_receive_event_storage_error():
    def get_failing_storage():
        mock_storage = MagicMock()
        mock_storage.store_event.return_value = False
        return mock_storage

    app.dependency_overrides[get_storage] = get_failing_storage

    response = client.post(
        "/event", json={"event_type": "message", "event_payload": "test"}
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to store event"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_receive_event_success():
    def get_successful_storage():
        mock_storage = MagicMock()
        mock_storage.store_event.return_value = True
        return mock_storage

    app.dependency_overrides[get_storage] = get_successful_storage

    response = client.post(
        "/event", json={"event_type": "message", "event_payload": "test"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Event stored successfully",
    }

    app.dependency_overrides.clear()
