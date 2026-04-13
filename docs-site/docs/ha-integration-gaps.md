# Home Assistant integration gaps

This page describes **what the GE Concord automation protocol delivers**, what **concord232** parses and stores, what the **HTTP API** exposes, and what the **built-in Home Assistant Concord232 integration** actually uses. Use it when planning automations (for example on **trouble** or **alarm** events) or when extending the server or API.

## What Home Assistant uses today

Home Assistant’s [Concord232 integration](https://www.home-assistant.io/integrations/concord232/) talks to the concord232 server over HTTP (default port **5007**) via the `concord232` Python **client** shipped with this project.

| Platform | Data source | What it uses |
|----------|-------------|--------------|
| **Alarm control panel** | `GET /partitions` | First partition only: **`arming_level`** → disarmed / armed home / armed away. |
| **Binary sensors (zones)** | `GET /zones` | Each zone’s **`state`** (and name, type, etc.): entity is “on” when `state != "Normal"`. |

Everything else the panel sends—unless it is reflected in those endpoints—is **not visible** to the stock integration.

**Note:** Zone `state` in the API is derived from protocol decoding and may be represented as a **list** of state strings (see `build_state_list` in `concord232/concord_commands.py`). The HA binary sensor code compares to the string `"Normal"`. If your entities behave unexpectedly, confirm the JSON shape returned by `/zones` and adjust either the API normalization or the integration.

## What the HTTP API exposes

Defined in `concord232/server/api.py`:

| Endpoint | Purpose |
|----------|---------|
| `/zones` | Zone list (subset of fields; bypass/condition flags are not included). |
| `/partitions` | Partition arming level and text. |
| `/panel` | Panel object from the controller (see gap below). |
| `/command` | Arm, disarm, keypresses. |
| `/version` | API version. |
| `/equipment` | Triggers equipment list request on the panel. |
| `/all_data` | Triggers dynamic data refresh request. |

There is **no** endpoint today for alarm/trouble events, touchpad text, delays, feature state, or a rolling event log.

**Partitions list vs partition `number` (custom integrations):** `GET /partitions` returns an array whose **length** is how many partitions the panel reports (often **1** on residential installs). Each entry includes **`number`**, the panel’s partition id (commonly **1** for the only partition). Do **not** use the panel id as a **zero-based array index**—for example, with a single partition, the only element is at **`partitions[0]`**, even though its `number` may be `1`. Using `partitions[1]` or `partitions[2]` when `len(partitions) == 1` leads to errors like *“partition index 1 not available (only 1 partition(s))”*. Match entities to rows by **`number`**, or cap configured partitions to what the API returns.

## Panel messages parsed but not passed through to HA

The following are handled (fully or partially) in `concord232/concord_commands.py` / `concord232/concord.py` but **do not** surface in a form Home Assistant can poll from the current API.

### High value for automations

1. **`ALARM` / Alarm–Trouble (`0x22` / `0x02`)**  
   Structured events: alarms, **system trouble**, fire / non-fire trouble, restorals, openings/closings, bypass events, and more—decoded via `cmd_alarm_trouble` and `concord232/concord_alarm_codes.py`.  
   **Gap (HTTP):** Results are not stored on the controller for the API; they appear in **debug logs** only unless you enable **MQTT** (see below). Many **system-level** troubles may **only** appear here, not as a zone state.

2. **`TOUCHPAD` (`0x22` / `0x09`)**  
   Keypad display text.  
   **Gap (HTTP):** Appended to `display_messages` on `AlarmPanelInterface`; **not** exposed by the API unless you enable **MQTT** (see below).

3. **Entry / exit delay (`0x22` / `0x03`)**  
   Countdown and delay flags.  
   **Gap:** Decoded but not persisted or exposed.

4. **`FEAT_STATE` (`0x22` / `0x0C`)**  
   Partition features (e.g. chime, quick arm, silent arming).  
   **Gap:** Decoded but not persisted or exposed.

### Panel maintenance and identity

5. **`PANEL_TYPE` (`0x01`)**  
   Panel type and serial.  
   **Gap:** `cmd_panel_type` returns a dict, but **`self.panel`** on the interface is never populated elsewhere, so **`/panel`** typically returns an empty object.

6. **`EVENT_LOST` (`0x02`)**  
   Automation buffer overflow; protocol docs expect a refresh.  
   **Gap:** Parser returns an empty dict; no automatic equipment/dynamic refresh is triggered from this message in code.

7. **`CLEAR_IMAGE` (`0x20`)**  
   Signal to reload equipment / state after power-up or programming exit.  
   **Gap:** Documented in the parser; no follow-up request is issued from the handler.

### Dropped or stubbed

8. **Siren and lights (early exit in `handle_message`)**  
   `SIREN_SYNC`, `SIREN_SETUP`, `SIREN_GO`, and `LIGHTS_STATE` are **not parsed**—`concord232/concord.py` returns before dispatching to the command parser.

9. **Equipment list detail commands**  
   SuperBus device data, capabilities, outputs, schedules, light attachments, etc.: many handlers are **stubs** or unparsed for automation purposes.

10. **`USER_DATA` (`0x09`)**  
    Parsed in `cmd_user_data` but **not** merged into `self.users` (which stays unused).

### API field trimming

Zone responses intentionally omit several in-memory concepts (see commented fields in `show_zone()` in `api.py`), such as bypass and condition flags, even where similar ideas exist in the wider codebase.

## Extension hooks

`AlarmPanelInterface.register_message_handler()` runs **after** each decoded message: registered handlers receive the same dict the parser returned (including `command_id`). The server uses this to optionally publish **`ALARM`** and **`TOUCHPAD`** to MQTT when `[mqtt]` / CLI broker settings are set—see `concord232/mqtt_events.py` and `concord232/main.py`.

## Possible directions

- **MQTT (supported):** When `--mqtt-host` or `[mqtt] host` is set, the server publishes JSON **schema v1** to `{topic_prefix}/event/alarm` and `{topic_prefix}/event/touchpad` (touchpad optional). Retained `{topic_prefix}/status` reports `online`. Configure the Home Assistant add-on with `mqtt_*` options or use `config.ini`. Details: [MQTT panel events design](mqtt-panel-events-design.md). For **separate Home Assistant entities per partition** on the shared `event/alarm` topic, see the operator’s **home-assistant-config** repo (`docs-site/docs/integrations/concord232-mqtt-partition-alarm-entities.md`); this repository keeps a [short pointer](ha-mqtt-partition-alarm-entities-design.md). If the broker requires a login (typical for the Mosquitto add-on or HA’s integrated broker), set **`mqtt_username` and `mqtt_password`** to the same values shown under **Settings → Devices & services → MQTT → Configure**; leaving them empty connects anonymously and the broker may log `not authorised` or `null username or password`.
- **HTTP:** Add endpoints such as `GET /events` (ring buffer) or `GET /last_alarm` and have HA poll them, or call an HA **webhook** from the server when `ALARM` is decoded.
- **Home Assistant core:** Extend the official integration once the API exposes stable event payloads (MQTT can be consumed today via the **MQTT** integration).

For serial setup and testing the automation link, see [Testing the Superbus Automation Module](testing-superbus.md) and [Migrating concord232 to Home Assistant Yellow](migration-mac-mini-to-ha-yellow.md).
