# Design: MQTT panel events for Concord232

**Date:** 2026-04-13  
**Status:** Implemented (server + add-on options)  
**Context:** Home Assistant already uses MQTT for lights and climate; extending the same broker for Concord alarm/trouble and keypad-derived information avoids a new integration surface and matches operator expectations.

## Problem

The GE Concord 4 reports conditions such as bus faults and multi-keypad protest text (for example “Sensor 07 Open”) through the automation protocol. The stock Home Assistant `concord232` integration only consumes `GET /partitions` and `GET /zones`, so **alarm/trouble events** and **touchpad display text** never reach automations. The Superbus Automation Module is only the RS-232 link; the actionable data is in **protocol messages** the panel already sends.

## Goals

1. Make **decoded panel events** visible to Home Assistant (and other subscribers) **via MQTT**, reusing the household broker.
2. Prefer **push** (publish on decode) over polling HTTP for time-sensitive faults and protest text.
3. Keep payloads **stable JSON** suitable for MQTT Device Trigger / template sensors / Node-RED.
4. **Minimize scope:** implement what the library already parses well before investing in Superbus equipment-list binary parsers.

## Non-goals (initial release)

- Parsing **SuperBus Device Data / Capabilities** responses (`cmd_superbus_dev_data` / `cmd_superbus_dev_cap` are currently stubs). Defer until a concrete need and protocol byte layouts are pinned.
- Replacing the official HTTP-based HA integration for arming/zone state (may remain as-is; MQTT supplements it).
- Full **Home Assistant core** changes; consumption can start with **MQTT integration** primitives.

## What the protocol already provides (relevant)

| Message | ID | Use |
|--------|-----|-----|
| Alarm / trouble | `0x22` / `0x02` (`ALARM`) | Structured source (e.g. Bus Device, Zone, System), source number, general/specific trouble types (e.g. system trouble including bus-related faults). |
| Touchpad display | `0x22` / `0x09` (`TOUCHPAD`) | Human-readable lines such as protest strings; stored today in `display_messages`, not exposed on the API. |
| Zone status / data | `0x21`, `0x03` | Already drives `/zones`; optional to mirror on MQTT for consistency. |

Reference: [Home Assistant integration gaps](ha-integration-gaps.md).

## Architecture

```mermaid
flowchart LR
  Panel[Concord 4 panel]
  SAM[Superbus Automation Module]
  SRV[concord232 server]
  MQTT[MQTT broker]
  HA[Home Assistant]

  Panel --> SAM --> SRV
  SRV -->|publish JSON| MQTT --> HA
```

1. **Serial path unchanged:** SAM → existing `AlarmPanelInterface` parse loop.
2. **After** a command parser returns a dict, the server **publishes** one (or few) MQTT messages with a small JSON body.
3. **Fix `register_message_handler`:** today the loop logs “Calling handler” but does not invoke `handler(decoded_command)`. Registered handlers should receive the same `decoded_command` dict (including `command_id`) so MQTT (or tests) can subscribe without patching parsers.

## MQTT topic layout

Use a configurable **topic prefix** (default suggestion: `concord232` or `home/concord232`).

| Topic pattern | Retain | Purpose |
|---------------|--------|---------|
| `{prefix}/status` | yes | JSON: `online` / connection state; optional `last_error` (broker LWT can mirror `offline`). |
| `{prefix}/event/alarm` | no | One message per decoded `ALARM` / trouble frame. |
| `{prefix}/event/touchpad` | no | One message per `TOUCHPAD` update (may be frequent; consider optional throttle later). |
| `{prefix}/event/zone` | no | *Optional phase:* zone snapshot deltas if we want parity with HTTP without polling. |

Version the payload with a top-level **`schema_version`** integer (start at `1`).

## JSON payload (schema v1)

### `event/alarm`

Mirror fields produced by `cmd_alarm_trouble` plus normalized names:

- `schema_version`, `command_id` (`ALARM`)
- `partition_number`, `area_number`
- `source_type`, `source_number` (numeric)
- `alarm_general_type`, `alarm_specific_type` (human-readable strings from `decode_alarm_type`)
- `alarm_general_type_code`, `alarm_specific_type_code`
- `event_specific_data` (integer)
- `received_at` (ISO 8601 UTC from server)

### `event/touchpad`

- `schema_version`, `command_id` (`TOUCHPAD`)
- `partition_number`, `area_number`, `message_type`
- `display_text` (string)
- `received_at`

Avoid embedding large history; consumers keep their own if needed.

## Configuration

Add server-side settings (environment or config file, consistent with existing server patterns):

- MQTT **broker** host, port, TLS, username/password.
- **Topic prefix**.
- Enable/disable **touchpad** publishes (high volume on some panels).
- Optional: **client_id** for the concord232 publisher.

## Home Assistant consumption (informal)

Not part of this repository’s core deliverable, but operators typically:

- **Automations:** `mqtt` trigger on `event/alarm` topic with JSON template conditions on `alarm_general_type` / `source_type`.
- **Template sensors:** map JSON attributes from the same topic.
- **Device triggers:** if using MQTT Device Trigger format later, that can be a follow-on enhancement.

## Error handling and resilience

- MQTT publish failures should **log** and optionally **queue** with a small bounded buffer; do not block the serial loop indefinitely.
- On serial reconnect, publish **`online`** to `{prefix}/status` (retained).
- Consider **EVENT_LOST** / **CLEAR_IMAGE** panel messages: future work may trigger `request_dynamic_data_refresh` + equipment list (see gaps doc); not required for first MQTT drop.

## Testing

- Unit tests: mock MQTT client; assert publish called with expected topic and JSON for synthetic `inject_alarm_message` / injected touchpad frames.
- Integration: run against `scripts/test_superbus.py` or panel with `--debug` and verify broker receives messages when faults are provoked.

## Security

- Use TLS to the broker when exposed beyond localhost; reuse same credentials pattern as existing MQTT clients in the home.

## Open decisions

1. **Throttle / dedupe** touchpad publishes (e.g. identical text within 1 s) — start without, add if needed.
2. Whether to publish **retained last alarm** on `{prefix}/event/alarm/last` for late subscribers (nice-to-have).

---

After this design is approved, the implementation plan should cover: handler invocation fix, MQTT client wiring, configuration, and tests as above.
