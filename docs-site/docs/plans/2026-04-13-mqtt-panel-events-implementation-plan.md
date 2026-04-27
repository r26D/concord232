# MQTT panel events Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish decoded Concord `ALARM` and `TOUCHPAD` events to MQTT as JSON (schema v1), fix `register_message_handler` so callbacks actually run, and make MQTT optional via config so existing installs stay unchanged.

**Architecture:** Keep the serial/parser path in `AlarmPanelInterface` unchanged. After `command_parser` returns a dict, invoke each registered handler with that dict. A small `PanelMqttPublisher` class (new module) subscribes to `ALARM` / `TOUCHPAD` handlers and publishes to `{prefix}/event/alarm` and `{prefix}/event/touchpad` using **paho-mqtt**. Connection and topic prefix come from `config.ini` `[mqtt]` and optional CLI overrides in `main.py`. The Home Assistant add-on passes MQTT settings through `options.json` → `run.sh` → CLI.

**Tech stack:** Python 3.6+, Flask (existing), **paho-mqtt** (new dependency), `configparser`, `pytest`.

**Spec:** [mqtt-panel-events-design.md](../mqtt-panel-events-design.md)

---

## File map

| File | Role |
|------|------|
| `concord232/concord.py` | Fix handler loop in `handle_message` to call each `handler(decoded_command)`. |
| `concord232/mqtt_events.py` (new) | Build JSON payloads (`schema_version: 1`), publish to MQTT, retained `{prefix}/status`. |
| `concord232/main.py` | Parse `[mqtt]` config and CLI; construct `PanelMqttPublisher` when enabled; register handlers after `AlarmPanelInterface` is created. |
| `pyproject.toml` | Add dependency `paho-mqtt` (use a 1.x line if maintaining broad Python support, e.g. `paho-mqtt>=1.6.1,<2`). |
| `tests/concord/test_message_handlers.py` (new) | Prove handlers run for `ALARM` with a checksummed synthetic frame. |
| `tests/concord/test_mqtt_events.py` (new) | Mock MQTT client; assert topic + JSON body for alarm and touchpad payloads. |
| `addon_concord232/config.yaml` | Optional MQTT options + schema. |
| `addon_concord232/run.sh` | Pass MQTT flags from `jq` when set. |
| `docs-site/docs/ha-integration-gaps.md` | Short note that MQTT can expose events (post-implementation). |

---

### Task 1: Invoke registered message handlers

**Files:**
- Modify: `concord232/concord.py` (inside `handle_message`, after `decoded_command` is built and not short-circuited)
- Create: `tests/concord/test_message_handlers.py`

- [ ] **Step 1: Write the failing test**

```python
import logging

import pytest

from concord232.concord import AlarmPanelInterface
from concord232.concord_commands import build_cmd_alarm_trouble
from concord232.concord import compute_checksum


def test_alarm_message_handler_receives_decoded_command():
    log = logging.getLogger("test")
    panel = AlarmPanelInterface("fake", 0.25, log)
    seen = []

    def capture(cmd: dict) -> None:
        seen.append(cmd)

    panel.register_message_handler("ALARM", capture)

    msg = build_cmd_alarm_trouble(1, "System", 1, 15, 21)
    msg.append(compute_checksum(msg))
    panel.handle_message(msg)

    assert len(seen) == 1
    assert seen[0]["command_id"] == "ALARM"
    assert seen[0]["alarm_general_type"] == "System Trouble"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/concord/test_message_handlers.py::test_alarm_message_handler_receives_decoded_command -v`

Expected: **FAIL** (handler never appended to `seen` until loop calls `handler(decoded_command)`).

- [ ] **Step 3: Minimal implementation**

In `concord232/concord.py`, replace the handler loop that only logs with an actual call:

```python
            for handler in self.message_handlers[command_id]:
                self.logger.debug("Calling handler %r" % handler)
                handler(decoded_command)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/concord/test_message_handlers.py::test_alarm_message_handler_receives_decoded_command -v`

Expected: **PASS**

- [ ] **Step 5: Commit**

```bash
git add concord232/concord.py tests/concord/test_message_handlers.py
git commit -m "fix: invoke AlarmPanelInterface message handlers with decoded commands"
```

---

### Task 2: JSON payloads and MQTT publisher module

**Files:**
- Create: `concord232/mqtt_events.py`
- Create: `tests/concord/test_mqtt_events.py`
- Modify: `pyproject.toml` (dependencies)

- [ ] **Step 1: Add dependency**

In `[project]` `dependencies` add:

```toml
    "paho-mqtt>=1.6.1,<2",
```

Run: `uv lock` or `pip install -e '.[dev]'` per project convention so tests can import `paho`.

- [ ] **Step 2: Write failing tests for payload shape (no broker)**

`tests/concord/test_mqtt_events.py`:

```python
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from concord232.mqtt_events import PanelMqttPublisher, build_alarm_payload, build_touchpad_payload


def test_build_alarm_payload_schema_v1():
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
    body = build_alarm_payload(decoded, received_at=datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc))
    assert body["schema_version"] == 1
    assert body["command_id"] == "ALARM"
    assert body["source_number"] == 6
    assert body["received_at"] == "2026-04-13T12:00:00+00:00"


def test_publish_alarm_uses_topic_prefix():
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
    with patch("concord232.mqtt_events.datetime") as dt_mod:
        fixed = datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)
        dt_mod.now.return_value = fixed
        pub.publish_alarm(decoded)
    mock_client.publish.assert_called_once()
    args, kwargs = mock_client.publish.call_args
    assert args[0] == "home/concord232/event/alarm"
    loaded = json.loads(args[1])
    assert loaded["schema_version"] == 1
    assert kwargs.get("qos", 1) == 1
```

Adjust imports if you name helpers differently; the test must fail until `PanelMqttPublisher` and helpers exist.

- [ ] **Step 3: Run tests — expect failure**

Run: `pytest tests/concord/test_mqtt_events.py -v`

Expected: **ImportError** or **AttributeError**.

- [ ] **Step 4: Implement `concord232/mqtt_events.py`**

- `build_alarm_payload` / `build_touchpad_payload`: add `schema_version: 1`, normalize `received_at` with `datetime.now(timezone.utc).isoformat()`.
- Strip or serialize `timestamp` on touchpad dicts (parser uses `datetime` in `cmd_touchpad`) to ISO strings in the MQTT JSON only.
- `PanelMqttPublisher.__init__(self, client, topic_prefix, publish_touchpad=True)`: store client and prefix; methods `publish_alarm`, `publish_touchpad`, `publish_online`.
- `publish_*` calls `self._client.publish(topic, json.dumps(payload), qos=1, retain=False)` for events; `publish_online` publishes retained JSON `{"state": "online", "schema_version": 1}` to `{prefix}/status`.
- Do not block the serial thread on network I/O longer than necessary: use the synchronous client in a tight loop is acceptable for v1; if publish raises, log and continue.

- [ ] **Step 5: Run tests — expect pass**

Run: `pytest tests/concord/test_mqtt_events.py -v`

- [ ] **Step 6: Commit**

```bash
git add concord232/mqtt_events.py tests/concord/test_mqtt_events.py pyproject.toml
git commit -m "feat: MQTT JSON payloads and PanelMqttPublisher"
```

---

### Task 3: Wire MQTT in `main.py` and config

**Files:**
- Modify: `concord232/main.py`

- [ ] **Step 1: Extend config reading**

- Add optional CLI flags: `--mqtt-host`, `--mqtt-port`, `--mqtt-username`, `--mqtt-password`, `--mqtt-prefix`, `--mqtt-disable-touchpad`, or rely on `[mqtt]` in the same `config.ini` as `[server]`.
- Recommended `[mqtt]` keys: `enabled` (bool), `host`, `port` (default 1883), `username`, `password`, `topic_prefix` (default `concord232`), `publish_touchpad` (default true), `tls` (bool, optional v1), `client_id` (optional).

- [ ] **Step 2: Connect publisher after panel creation**

After `ctrl = concord.AlarmPanelInterface(serial, 0.25, LOG)` and `api.CONTROLLER = ctrl`, if MQTT enabled:

```python
import paho.mqtt.client as mqtt
from concord232.mqtt_events import PanelMqttPublisher

client = mqtt.Client(client_id=mqtt_client_id)
if mqtt_username:
    client.username_pw_set(mqtt_username, mqtt_password)
client.connect(mqtt_host, mqtt_port, 60)
client.loop_start()

publisher = PanelMqttPublisher(client=client, topic_prefix=topic_prefix, publish_touchpad=publish_touchpad)
publisher.publish_online()

ctrl.register_message_handler("ALARM", publisher.publish_alarm)
if publish_touchpad:
    ctrl.register_message_handler("TOUCHPAD", publisher.publish_touchpad)
```

Use `functools.partial` if methods need binding; ensure thread safety of `paho` `loop_start()` with the serial thread calling `publish` (documented as OK for basic publish).

- [ ] **Step 3: Manual smoke check**

Run server with MQTT pointed at a local Mosquitto; trigger `inject_alarm_message` or panel event; subscribe with `mosquitto_sub -t 'concord232/#' -v`.

- [ ] **Step 4: Commit**

```bash
git add concord232/main.py
git commit -m "feat: optional MQTT publishing for ALARM and TOUCHPAD"
```

---

### Task 4: Home Assistant add-on options

**Files:**
- Modify: `addon_concord232/config.yaml`
- Modify: `addon_concord232/run.sh`

- [ ] **Step 1: Add options** (example; keep defaults empty/disabled)

```yaml
  mqtt_host: ""
  mqtt_port: 1883
  mqtt_username: ""
  mqtt_password: ""
  mqtt_topic_prefix: concord232
  mqtt_publish_touchpad: true
schema:
  serial: str
  port: int
  log: str?
  mqtt_host: str?
  mqtt_port: int?
  mqtt_username: str?
  mqtt_password: password?
  mqtt_topic_prefix: str?
  mqtt_publish_touchpad: bool?
```

- [ ] **Step 2: Extend `run.sh`**

After `EXTRA` for log, add `jq` reads for mqtt fields and append `--mqtt-host`, etc., only when `mqtt_host` is non-empty.

- [ ] **Step 3: Commit**

```bash
git add addon_concord232/config.yaml addon_concord232/run.sh
git commit -m "feat(addon): optional MQTT settings for panel events"
```

---

### Task 5: Documentation touch-up

**Files:**
- Modify: `docs-site/docs/ha-integration-gaps.md`
- Modify: `docs-site/docs/mqtt-panel-events-design.md` (set **Status:** Implemented when done)

- [ ] **Step 1:** Add a subsection under “Possible directions” or “Extension hooks” noting MQTT topics and that `paho-mqtt` is optional at runtime for non-MQTT installs (if you split extras, document that).

- [ ] **Step 2: Commit**

```bash
git add docs-site/docs/ha-integration-gaps.md docs-site/docs/mqtt-panel-events-design.md
git commit -m "docs: MQTT panel events implementation notes"
```

---

## Spec coverage (self-review)

| Design section | Task |
|----------------|------|
| Fix `register_message_handler` | Task 1 |
| `{prefix}/event/alarm`, `{prefix}/event/touchpad`, `{prefix}/status` | Task 2–3 |
| Schema v1 JSON fields | Task 2 |
| Config (broker, prefix, touchpad toggle) | Task 3–4 |
| Non-blocking / log on publish failure | Task 2 (implement log in `publish_*`) |
| Tests | Tasks 1–2 |

**Placeholder scan:** No TBD/TODO left in tasks above.

**Type consistency:** `command_id` strings match `RX_COMMANDS` (`"ALARM"`, `"TOUCHPAD"`).

**Gap:** SuperBus device parsers remain stubbed — explicitly out of scope per design.

---

**Plan complete and saved to `docs-site/docs/plans/2026-04-13-mqtt-panel-events-implementation-plan.md`.**

The deprecated **`/write-plan`** Cursor command should not be used; use this **writing-plans** workflow instead.

**Two execution options:**

1. **Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration. **REQUIRED SUB-SKILL:** superpowers:subagent-driven-development.

2. **Inline execution** — Run tasks in this session using checkpoints. **REQUIRED SUB-SKILL:** superpowers:executing-plans.

**Which approach do you want?**
