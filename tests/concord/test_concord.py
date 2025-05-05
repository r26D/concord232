import pytest

from concord232.concord import (
    BadEncoding,
    compute_checksum,
    decode_message_from_ascii,
    encode_message_to_ascii,
    update_message_checksum,
    validate_message_checksum,
)


def test_compute_checksum():
    assert compute_checksum([1, 2, 3]) == 6
    assert compute_checksum([255, 1]) == 0


def test_validate_message_checksum():
    msg = [2, 3, 5]  # 2+3=5, so checksum is 5
    assert validate_message_checksum(msg)
    msg = [2, 3, 6]
    assert not validate_message_checksum(msg)


def test_update_message_checksum():
    msg = [2, 3, 0]
    update_message_checksum(msg)
    assert msg[-1] == 5


def test_encode_message_to_ascii():
    assert encode_message_to_ascii([10, 255]) == "0AFF"


def test_decode_message_from_ascii():
    assert decode_message_from_ascii("0AFF") == [10, 255]
    with pytest.raises(BadEncoding):
        decode_message_from_ascii("0AF")  # Odd length
