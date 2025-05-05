import pytest

from concord232 import concord_commands
from concord232.concord_commands import KEYPRESS_CODES
from concord232.concord_helpers import BadMessageException


def test_keypress_codes():
    assert KEYPRESS_CODES[0x00] == "0"
    assert KEYPRESS_CODES[0x0A] == "*"
    assert KEYPRESS_CODES[0x1C] == "Fire TP - Acknowledge"


def test_ck_msg_len_exact():
    # Should not raise
    concord_commands.ck_msg_len([0] * 5, 0x01, 4)


def test_ck_msg_len_at_least():
    # Should not raise
    concord_commands.ck_msg_len([0] * 6, 0x01, 4, exact_len=False)


def test_ck_msg_len_too_short():
    with pytest.raises(BadMessageException):
        concord_commands.ck_msg_len([0] * 3, 0x01, 4)


def test_bytes_to_num():
    assert concord_commands.bytes_to_num([0, 0, 0, 1]) == 1
    assert concord_commands.bytes_to_num([0, 0, 1, 0]) == 256
    assert concord_commands.bytes_to_num([1, 0, 0, 0]) == 16777216


def test_num_to_bytes():
    assert concord_commands.num_to_bytes(1) == [0, 0, 0, 1]
    assert concord_commands.num_to_bytes(256) == [0, 0, 1, 0]
    assert concord_commands.num_to_bytes(16777216) == [1, 0, 0, 0]


def test_build_state_list():
    d = {0: "A", 1: "B"}
    assert concord_commands.build_state_list(1, d) == ["B"]
    assert concord_commands.build_state_list(2, d) == ["Unknown"]


def test_decode_alarm_type():
    # Use a known code from ALARM_CODES
    from concord232.concord_alarm_codes import ALARM_SPECIFIC_TYPES

    concord_commands.ALARM_CODES = {1: ("General", ALARM_SPECIFIC_TYPES)}
    assert concord_commands.decode_alarm_type(1, 1) == ("General", "Fire")
    assert concord_commands.decode_alarm_type(99, 1) == ("Unknown", "Unknown")


def test_bcd_decode():
    # BCD for 12 is 0x12
    assert concord_commands.bcd_decode([0x12]) == 12
    # BCD for 45 is 0x45
    assert concord_commands.bcd_decode([0x45]) == 45
