# Design: Per-partition alarm/trouble entities in Home Assistant (MQTT)

**Date:** 2026-04-13  
**Status:** Agreed (Home Assistant configuration; no concord232 code change required)  
**Depends on:** [MQTT panel events design](mqtt-panel-events-design.md), [Home Assistant integration gaps](ha-integration-gaps.md)

## Problem

The concord232 server publishes decoded **`ALARM`** frames (alarms, **system trouble**, restorals, and related event types) to a **single** MQTT topic: `{topic_prefix}/event/alarm`. Payloads are JSON **schema v1** and include **`partition_number`**, but the topic path does **not** vary by partition.

Installations with **multiple partitions** need **separate Home Assistant entities** per partition so automations and dashboards can target partition 1, 2, and 3 without multiplexing “last message from anywhere” into one sensor state.

## Goals

1. Provide **three distinct entities** (one per partition), each reflecting **that partition’s** most recent alarm/trouble-related event fields exposed for automations.
2. Use **idiomatic Home Assistant** patterns: real entities with stable `entity_id`s, not only raw MQTT inspection.
3. Avoid requiring a concord232 release for this phase (consume the existing topic and JSON shape).

## Non-goals (this document)

- Defining panel-specific rules for **latched** “trouble still active” vs **restoral** messages (depends on `alarm_general_type` / codes in your traffic; add later via automations or template logic).
- Changing MQTT topics in concord232 (optional future enhancement; see below).

## Constraints

- Messages on `event/alarm` are **not retained**; HA only sees **new** publishes after the MQTT connection is up.
- A plain **single** [`mqtt` sensor](https://www.home-assistant.io/integrations/sensor.mqtt/) on `…/event/alarm` updates from **every** partition; its **state** always reflects the **last** message globally. **Do not** use one such sensor as the sole per-partition model without filtering.

## Recommended approach: trigger-based template sensors

Use **three** [trigger-based template](https://www.home-assistant.io/integrations/template/#trigger-based-template-binary-sensors-sensors-and-cover) **sensors** (or **binary sensors** if you later map clear on/off rules), each with:

- **Trigger:** MQTT on `{topic_prefix}/event/alarm` (same topic for all three).
- **State / attributes:** Set from `trigger.payload_json` **only when** `partition_number` matches **1**, **2**, or **3** respectively; when the message is for another partition, **preserve** the previous state/attributes (template expression referencing prior state, per HA trigger-template patterns).

Each entity should expose at least:

- A short **state** string suitable for display (for example `alarm_general_type` and `alarm_specific_type`, or a single combined string).
- **Attributes** mirroring schema v1 fields you care about: `source_type`, `source_number`, `alarm_general_type`, `alarm_specific_type`, codes, `event_specific_data`, `received_at`, and `partition_number` for debugging.

Naming: use clear names and, if you use **Devices & areas**, assign each sensor to the right **area** matching the partition.

## Alternative: MQTT automations and helpers

For operators who prefer explicit automation graphs:

- **Automation** with [`mqtt` trigger](https://www.home-assistant.io/docs/automation/trigger/#mqtt-trigger) on `…/event/alarm`, **condition** `payload_json.partition_number == N`, **action** `input_text.set_value` / `input_datetime.set_datetime` / `input_boolean` per partition.

This is equally valid; slightly more YAML and moving parts than trigger templates, but very clear.

## Optional future: publisher topic split

If concord232 later publishes to `{topic_prefix}/event/alarm/{partition_number}` (or similar), each partition could use a **simple** `mqtt` sensor with its own `state_topic` without trigger filtering. That would be a **concord232** change; not required for the patterns above.

## Testing

1. In HA **Developer tools → MQTT**, subscribe to `{topic_prefix}/event/alarm` and confirm JSON includes the expected `partition_number` when you provoke faults on each partition.
2. Confirm each of the three entities updates **only** when its partition appears in the payload, and **does not** change when another partition’s message arrives.

## References

- Payload fields: `build_alarm_payload()` in `concord232/mqtt_events.py`.
- Topic layout: [MQTT panel events design](mqtt-panel-events-design.md).
