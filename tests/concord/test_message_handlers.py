import logging
from typing import Any, List

from concord232.concord import AlarmPanelInterface, compute_checksum
from concord232.concord_commands import build_cmd_alarm_trouble


def test_alarm_message_handler_receives_decoded_command() -> None:
    log = logging.getLogger("test")
    panel = AlarmPanelInterface("fake", 0.25, log)
    seen: List[Any] = []

    def capture(cmd: dict) -> None:
        seen.append(cmd)

    panel.register_message_handler("ALARM", capture)

    msg = build_cmd_alarm_trouble(1, "System", 1, 15, 21)
    msg.append(compute_checksum(msg))
    panel.handle_message(msg)

    assert len(seen) == 1
    assert seen[0]["command_id"] == "ALARM"
    assert seen[0]["alarm_general_type"] == "System Trouble"
