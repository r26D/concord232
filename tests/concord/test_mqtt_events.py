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


def test_build_zone_payload_mirrors_rest_fields() -> None:
    from concord232.mqtt_events import build_zone_payload

    zone = {
        "partition_number": 1,
        "area_number": 0,
        "group_number": 10,
        "zone_number": 1,
        "zone_type": "Hardwired",
        "zone_state": ["Tripped"],
        "zone_text": "FRONT DOOR",
    }
    body = build_zone_payload(
        zone, received_at=datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)
    )
    assert body["schema_version"] == 1
    assert body["partition"] == 1
    assert body["group"] == 10
    assert body["number"] == 1
    assert body["name"] == "FRONT DOOR"
    assert body["state"] == ["Tripped"]
    assert body["type"] == "Hardwired"
    assert body["tripped"] is True
    assert body["received_at"] == "2026-04-13T12:00:00+00:00"


def test_build_zone_payload_tripped_with_multiple_states() -> None:
    from concord232.mqtt_events import build_zone_payload

    body = build_zone_payload({"zone_number": 2, "zone_state": ["Trouble", "Tripped"]})
    assert body["tripped"] is True
    body = build_zone_payload({"zone_number": 2, "zone_state": ["Normal"]})
    assert body["tripped"] is False


def test_publish_zone_retained_state_and_single_discovery() -> None:
    client = MagicMock()
    pub = PanelMqttPublisher(
        client,
        "concord232",
        publish_zones=True,
        discovery_prefix="homeassistant",
    )
    zone = {
        "partition_number": 1,
        "zone_number": 1,
        "zone_state": ["Tripped"],
        "zone_text": "FRONT DOOR",
        "zone_type": "Hardwired",
    }
    pub.publish_zone(zone)
    pub.publish_zone(zone)

    calls = client.publish.call_args_list
    state_calls = [c for c in calls if c.args[0] == "concord232/zone/1/state"]
    config_calls = [
        c
        for c in calls
        if c.args[0] == "homeassistant/binary_sensor/concord232/zone_1/config"
    ]
    assert len(state_calls) == 2
    assert all(c.kwargs["retain"] is True for c in state_calls)
    assert len(config_calls) == 1
    config = json.loads(config_calls[0].args[1])
    assert config["unique_id"] == "concord232_zone_1"
    assert config["name"] == "Front Door"
    assert config["state_topic"] == "concord232/zone/1/state"
    assert "value_json.tripped" in config["value_template"]
    assert config["availability"][0]["topic"] == "concord232/status"
    state = json.loads(state_calls[0].args[1])
    assert state["tripped"] is True


def test_publish_zone_noop_when_disabled() -> None:
    client = MagicMock()
    pub = PanelMqttPublisher(client, "concord232", publish_zones=False)
    pub.publish_zone({"zone_number": 1, "zone_state": ["Normal"]})
    client.publish.assert_not_called()


def test_make_zone_handler_prefers_merged_record() -> None:
    from concord232.mqtt_events import make_zone_handler

    client = MagicMock()
    pub = PanelMqttPublisher(client, "concord232", publish_zones=True)
    zones = {
        "p1z1": {
            "partition_number": 1,
            "zone_number": 1,
            "zone_state": ["Tripped"],
            "zone_text": "FRONT DOOR",
            "zone_type": "Hardwired",
        }
    }
    handler = make_zone_handler(pub, zones)
    # ZONE_STATUS decode carries no name; the merged record must win.
    handler({"partition_number": 1, "zone_number": 1, "zone_state": ["Tripped"]})
    state = json.loads(client.publish.call_args_list[0].args[1])
    assert state["name"] == "FRONT DOOR"

    # Unknown zone falls back to the decoded message.
    handler({"partition_number": 1, "zone_number": 9, "zone_state": ["Normal"]})
    fallback = json.loads(client.publish.call_args_list[-1].args[1])
    assert fallback["number"] == 9
    assert fallback["name"] == ""
