"""
Helper functions and exceptions for concord232, including hex/ascii conversion and timedelta utilities.
"""


class BadMessageException(Exception):
    """Raised when a message is malformed or invalid."""

    pass


def ascii_hex_to_byte(ascii_bytes):
    """
    Convert two ASCII hex characters to a single byte integer.
    Args:
        ascii_bytes (str or list): Two ASCII characters representing a hex value.
    Returns:
        int: Integer value of the hex byte.
    Raises:
        ValueError: If the input cannot be parsed as hex.
    """
    assert len(ascii_bytes) >= 2
    return int(ascii_bytes[0] + ascii_bytes[1], 16)


def total_secs(td):
    """
    Convert a timedelta object to total seconds (float).
    Args:
        td (datetime.timedelta): The timedelta to convert.
    Returns:
        float: Total seconds represented by the timedelta.
    """
    return td.days * 3600 * 24 + td.seconds + td.microseconds / 1.0e6
