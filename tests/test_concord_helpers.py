import pytest
from concord232.concord_helpers import ascii_hex_to_byte, total_secs

def test_ascii_hex_to_byte():
    assert ascii_hex_to_byte(['3', 'A']) == 0x3A
    assert ascii_hex_to_byte(['0', '0']) == 0x00
    assert ascii_hex_to_byte(['F', 'F']) == 0xFF

def test_total_secs():
    from datetime import timedelta
    assert total_secs(timedelta(seconds=5)) == 5
    assert total_secs(timedelta(minutes=2, seconds=3)) == 123 