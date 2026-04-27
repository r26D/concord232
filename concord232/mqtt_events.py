"""
MQTT publishing for Concord panel events (ALARM / TOUCHPAD), schema version 1.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

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


class PanelMqttPublisher:
    """Publishes panel decode dicts to MQTT topics under a prefix."""

    def __init__(
        self,
        client: Any,
        topic_prefix: str,
        *,
        publish_touchpad: bool = True,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._client = client
        self._prefix = topic_prefix.strip().strip("/")
        # Must not shadow method publish_touchpad (used as a message handler callback).
        self._touchpad_enabled = publish_touchpad
        self._log = logger or LOG

    def _topic(self, *parts: str) -> str:
        return "/".join((self._prefix,) + parts)

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

    def _publish_json(self, topic: str, payload: Mapping[str, Any], retain: bool) -> None:
        try:
            body = json.dumps(payload, default=str, separators=(",", ":"))
            self._client.publish(topic, body, qos=1, retain=retain)
        except Exception:
            self._log.exception("MQTT publish failed topic=%s", topic)
