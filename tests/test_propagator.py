import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from cybercare.propagator import load_events, send_event


class TestEventPropagator(unittest.TestCase):
    def setUp(self):
        self.test_events = [
            {"event_type": "message", "event_payload": "test"},
            {"event_type": "user_joined", "event_payload": "TestUser"},
        ]

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        json.dump(self.test_events, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_load_events(self):
        events = load_events(self.temp_file.name)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event_type"], "message")
        self.assertEqual(events[0]["event_payload"], "test")
        self.assertEqual(events[1]["event_type"], "user_joined")
        self.assertEqual(events[1]["event_payload"], "TestUser")

    def test_load_events_nonexistent_file(self):
        events = load_events("nonexistent_file.json")
        self.assertEqual(events, [])

    def test_load_events_invalid_json(self):
        invalid_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        invalid_file.write("This is not valid JSON")
        invalid_file.close()

        events = load_events(invalid_file.name)
        self.assertEqual(events, [])

        os.unlink(invalid_file.name)

    @patch("requests.post")
    def test_send_event_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        event = {"event_type": "message", "event_payload": "test"}
        result = send_event(event, "http://test-endpoint/event")

        self.assertTrue(result)
        mock_post.assert_called_once_with(
            "http://test-endpoint/event", json=event, timeout=10
        )

    @patch("requests.post")
    def test_send_event_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        event = {"event_type": "message", "event_payload": "test"}
        result = send_event(event, "http://test-endpoint/event")

        self.assertFalse(result)
        mock_post.assert_called_once_with(
            "http://test-endpoint/event", json=event, timeout=10
        )

    @patch("requests.post")
    def test_send_event_exception(self, mock_post):
        mock_post.side_effect = Exception("Connection error")

        event = {"event_type": "message", "event_payload": "test"}
        result = send_event(event, "http://test-endpoint/event")

        self.assertFalse(result)
        mock_post.assert_called_once_with(
            "http://test-endpoint/event", json=event, timeout=10
        )

    @patch("requests.post")
    def test_send_event_with_custom_timeout(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        event = {"event_type": "message", "event_payload": "test"}
        custom_timeout = 5
        result = send_event(event, "http://test-endpoint/event", timeout=custom_timeout)

        self.assertTrue(result)
        mock_post.assert_called_once_with(
            "http://test-endpoint/event", json=event, timeout=custom_timeout
        )
