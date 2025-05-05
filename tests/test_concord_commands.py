import pytest
from concord232.concord_commands import KEYPRESS_CODES, bytes_to_num

def test_keypress_codes():
    assert KEYPRESS_CODES[0x00] == '0'
    assert KEYPRESS_CODES[0x0a] == '*'
    assert KEYPRESS_CODES[0x1c] == 'Fire TP - Acknowledge'

def test_bytes_to_num():
    assert bytes_to_num([0, 0, 0, 1]) == 1
    assert bytes_to_num([0, 0, 1, 0]) == 256
    assert bytes_to_num([0, 1, 0, 0]) == 65536
    assert bytes_to_num([1, 0, 0, 0]) == 16777216 