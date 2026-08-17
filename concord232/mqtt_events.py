"""
MQTT publishing for Concord panel events (ALARM / TOUCHPAD) and retained
zone states, schema version 1.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from typing import Any, Optional

LOG = logging.getLogger(__name__)

SCHEMA_VERSION = 1


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def build_alarm_payload(
    decoded: Mapping[str, Any],
    *,
    received_at: Optional[datetime] = None,
) -> dict[str, Any]:
    when = received_at if received_at is not None else _utc_now()
    return {
        "schema_version": SCHEMA_VERSION,
        "command_id": decoded.get("command_id"),
        "partition_number": decoded.get("partition_number"),
        "area_number": decoded.get("area_number"),
        "source_type": decoded.get("source_type"),
        "source_number": decoded.get("source_number"),
        "alarm_general_type": decoded.get("alarm_general_type"),
        "alarm_specific_type": decoded.get("alarm_specific_type"),
        "alarm_general_type_code": decoded.get("alarm_general_type_code"),
        "alarm_specific_type_code": decoded.get("alarm_specific_type_code"),
        "event_specific_data": decoded.get("event_specific_data"),
        "received_at": _iso(when),
    }


def build_touchpad_payload(
    decoded: Mapping[str, Any],
    *,
    received_at: Optional[datetime] = None,
) -> dict[str, Any]:
    when = received_at if received_at is not None else _utc_now()
    ts = decoded.get("timestamp")
    panel_ts: Optional[str] = None
    if isinstance(ts, datetime):
        panel_ts = _iso(ts)
    body: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command_id": decoded.get("command_id"),
        "partition_number": decoded.get("partition_number"),
        "area_number": decoded.get("area_number"),
        "message_type": decoded.get("message_type"),
        "display_text": decoded.get("display_text"),
        "received_at": _iso(when),
    }
    if panel_ts is not None:
        body["panel_timestamp"] = panel_ts
    return body


def build_zone_payload(
    zone: Mapping[str, Any],
    *,
    received_at: datetime | None = None,
) -> dict[str, Any]:
    """Mirror of the ``/zones`` REST field names, plus a ``tripped`` bool."""
    when = received_at if received_at is not None else _utc_now()
    state = list(zone.get("zone_state") or [])
    return {
        "schema_version": SCHEMA_VERSION,
        "partition": zone.get("partition_number"),
        "area": zone.get("area_number"),
        "group": zone.get("group_number"),
        "number": zone.get("zone_number"),
        "name": zone.get("zone_text") or "",
        "state": state,
        "type": zone.get("zone_type"),
        "tripped": "Tripped" in state,
        "received_at": _iso(when),
    }


def make_zone_handler(
    publisher: PanelMqttPublisher,
    zones: Mapping[str, Mapping[str, Any]],
) -> Callable[[Mapping[str, Any]], None]:
    """Build a ZONE_STATUS / ZONE_DATA message handler.

    The decoded ZONE_STATUS message lacks name/type/group, so publish the
    merged record from the panel interface's live ``zones`` store (updated
    by the command parsers before handlers run), falling back to the
    decoded message for zones not yet in the store.
    """

    def _handle(decoded: Mapping[str, Any]) -> None:
        identifier = (
            f"p{decoded.get('partition_number')}z{decoded.get('zone_number')}"
        )
        publisher.publish_zone(zones.get(identifier, decoded))

    return _handle


class PanelMqttPublisher:
    """Publishes panel decode dicts to MQTT topics under a prefix."""

    def __init__(
        self,
        client: Any,
        topic_prefix: str,
        *,
        publish_touchpad: bool = True,
        publish_zones: bool = False,
        discovery_prefix: str | None = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._client = client
        self._prefix = topic_prefix.strip().strip("/")
        # Must not shadow method publish_touchpad (used as a message handler callback).
        self._touchpad_enabled = publish_touchpad
        self._zones_enabled = publish_zones
        self._discovery_prefix = (discovery_prefix or "").strip().strip("/")
        self._discovered_zones: set[int] = set()
        self._log = logger or LOG

    def _topic(self, *parts: str) -> str:
        return "/".join((self._prefix,) + parts)

    @property
    def status_topic(self) -> str:
        return self._topic("status")

    def publish_online(self) -> None:
        payload = json.dumps(
            {"schema_version": SCHEMA_VERSION, "state": "online"},
            separators=(",", ":"),
        )
        try:
            self._client.publish(
                self._topic("status"), payload, qos=1, retain=True
            )
        except Exception:
            self._log.exception("MQTT publish failed (status online)")

    def publish_alarm(self, decoded: Mapping[str, Any]) -> None:
        payload = build_alarm_payload(decoded)
        self._publish_json(self._topic("event", "alarm"), payload, retain=False)

    def publish_touchpad(self, decoded: Mapping[str, Any]) -> None:
        if not self._touchpad_enabled:
            return
        payload = build_touchpad_payload(decoded)
        self._publish_json(self._topic("event", "touchpad"), payload, retain=False)

    def publish_zone(self, zone: Mapping[str, Any]) -> None:
        """Publish a retained per-zone state (and discovery config, once)."""
        if not self._zones_enabled:
            return
        payload = build_zone_payload(zone)
        number = payload.get("number")
        if number is None:
            return
        self._publish_json(
            self._topic("zone", str(number), "state"), payload, retain=True
        )
        if self._discovery_prefix:
            self._publish_zone_discovery(payload)

    def _publish_zone_discovery(self, payload: Mapping[str, Any]) -> None:
        """Publish a Home Assistant MQTT discovery config for a zone, once."""
        number = payload["number"]
        if number in self._discovered_zones:
            return
        name = str(payload.get("name") or "").strip() or f"Zone {number}"
        config = {
            "name": name.title() if name.isupper() else name,
            "unique_id": f"concord232_zone_{number}",
            "state_topic": self._topic("zone", str(number), "state"),
            "value_template": "{{ 'ON' if value_json.tripped else 'OFF' }}",
            "json_attributes_topic": self._topic("zone", str(number), "state"),
            "availability": [
                {
                    "topic": self._topic("status"),
                    "value_template": "{{ value_json.state }}",
                    "payload_available": "online",
                    "payload_not_available": "offline",
                }
            ],
            "device": {
                "identifiers": ["concord232"],
                "name": "Concord232",
                "manufacturer": "GE Interlogix",
                "model": "Concord 4",
            },
        }
        topic = (
            f"{self._discovery_prefix}/binary_sensor/concord232/"
            f"zone_{number}/config"
        )
        self._publish_json(topic, config, retain=True)
        self._discovered_zones.add(number)

    def offline_payload(self) -> str:
        """Retained last-will payload marking the publisher offline."""
        return json.dumps(
            {"schema_version": SCHEMA_VERSION, "state": "offline"},
            separators=(",", ":"),
        )

    def _publish_json(self, topic: str, payload: Mapping[str, Any], retain: bool) -> None:
        try:
            body = json.dumps(payload, default=str, separators=(",", ":"))
            self._client.publish(topic, body, qos=1, retain=retain)
        except Exception:
            self._log.exception("MQTT publish failed topic=%s", topic)
