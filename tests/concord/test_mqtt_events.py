import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from concord232.mqtt_events import (
    PanelMqttPublisher,
    build_alarm_payload,
    build_touchpad_payload,
)


def test_build_alarm_payload_schema_v1() -> None:
    decoded = {
        "command_id": "ALARM",
        "partition_number": 1,
        "area_number": 0,
        "source_type": "Bus Device",
        "source_number": 6,
        "alarm_general_type": "System Trouble",
        "alarm_specific_type": "Bus Device Failure",
        "alarm_general_type_code": 15,
        "alarm_specific_type_code": 21,
        "event_specific_data": 0,
    }
    body = build_alarm_payload(
        decoded,
        received_at=datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc),
    )
    assert body["schema_version"] == 1
    assert body["command_id"] == "ALARM"
    assert body["source_number"] == 6
    assert body["received_at"] == "2026-04-13T12:00:00+00:00"


def test_build_touchpad_payload_serializes_panel_timestamp() -> None:
    ts = datetime(2026, 4, 13, 8, 30, 0, tzinfo=timezone.utc)
    decoded = {
        "command_id": "TOUCHPAD",
        "partition_number": 1,
        "area_number": 0,
        "message_type": "Normal",
        "display_text": "Sensor 07 Open",
        "timestamp": ts,
    }
    body = build_touchpad_payload(
        decoded,
        received_at=datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc),
    )
    assert body["panel_timestamp"] == "2026-04-13T08:30:00+00:00"
    assert body["display_text"] == "Sensor 07 Open"


def test_publish_alarm_uses_topic_prefix() -> None:
    mock_client = MagicMock()
    pub = PanelMqttPublisher(
        client=mock_client,
        topic_prefix="home/concord232",
    )
    decoded = {
        "command_id": "ALARM",
        "partition_number": 1,
        "area_number": 0,
        "source_type": "Bus Device",
        "source_number": 6,
        "alarm_general_type": "System Trouble",
        "alarm_specific_type": "Bus Device Failure",
        "alarm_general_type_code": 15,
        "alarm_specific_type_code": 21,
        "event_specific_data": 0,
    }
    fixed = datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)
    with patch("concord232.mqtt_events._utc_now", return_value=fixed):
        pub.publish_alarm(decoded)
    mock_client.publish.assert_called_once()
    args, kwargs = mock_client.publish.call_args
    assert args[0] == "home/concord232/event/alarm"
    loaded = json.loads(args[1])
    assert loaded["schema_version"] == 1
    assert loaded["received_at"] == "2026-04-13T12:00:00+00:00"
    assert kwargs.get("qos", 1) == 1


def test_publish_online_retained_status() -> None:
    mock_client = MagicMock()
    pub = PanelMqttPublisher(client=mock_client, topic_prefix="concord232")
    pub.publish_online()
    mock_client.publish.assert_called_once()
    args, kwargs = mock_client.publish.call_args
    assert args[0] == "concord232/status"
    assert json.loads(args[1])["state"] == "online"
    assert kwargs.get("retain") is True
