import datetime

import pytest

from concord232 import concord_helpers


def test_ascii_hex_to_byte_str():
    assert concord_helpers.ascii_hex_to_byte("1A") == 26


def test_ascii_hex_to_byte_list():
    assert concord_helpers.ascii_hex_to_byte(["1", "A"]) == 26


def test_ascii_hex_to_byte_invalid():
    with pytest.raises(ValueError):
        concord_helpers.ascii_hex_to_byte("ZZ")


def test_total_secs():
    td = datetime.timedelta(days=1, seconds=3661, microseconds=500000)
    assert concord_helpers.total_secs(td) == pytest.approx(90061.5)
