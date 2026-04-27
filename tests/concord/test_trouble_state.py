"""Tests for aggregated alarm/trouble state (e.g. multiple bus issues)."""

from concord232.concord import (
    _detail_from_trouble_store,
    _format_trouble_line_from_alarm,
    apply_alarm_to_trouble_store,
)


def _sys_trouble(bus: int, spec: int, specific_name: str) -> dict:
    return {
        "partition_number": 0,
        "area_number": 0,
        "source_type": "Bus Device",
        "source_number": bus,
        "alarm_general_type_code": 15,
        "alarm_specific_type_code": spec,
        "event_specific_data": 0,
        "alarm_general_type": "System Trouble",
        "alarm_specific_type": specific_name,
    }


def _sys_trouble_restoral(bus: int, spec: int, specific_name: str) -> dict:
    d = _sys_trouble(bus, spec, specific_name)
    d["alarm_general_type_code"] = 16
    d["alarm_general_type"] = "System Trouble Restoral"
    return d


def test_apply_adds_bus_troubles_shows_both_buses() -> None:
    store: dict = {}
    apply_alarm_to_trouble_store(store, _sys_trouble(1, 0, "Bus Receiver Failure"))
    apply_alarm_to_trouble_store(store, _sys_trouble(4, 21, "Bus Device Failure"))
    detail = _detail_from_trouble_store(store)
    assert "Bus 1:" in detail
    assert "Bus 4:" in detail
    assert "Bus Receiver Failure" in detail
    assert "Bus Device Failure" in detail


def test_format_non_bus_includes_source() -> None:
    s = _format_trouble_line_from_alarm(
        {
            "source_type": "System",
            "source_number": 1,
            "alarm_general_type": "System Trouble",
            "alarm_specific_type": "Main AC Failure",
        }
    )
    assert "System" in s
    assert "Main AC Failure" in s


def test_apply_restoral_clears_matching_trouble() -> None:
    store: dict = {}
    t = _sys_trouble(1, 0, "Bus Receiver Failure")
    r = _sys_trouble_restoral(1, 0, "Bus Receiver Failure")
    assert apply_alarm_to_trouble_store(store, t) is True
    assert len(store) == 1
    assert apply_alarm_to_trouble_store(store, r) is True
    assert store == {}


def test_idempotent_repeated_trouble() -> None:
    store: dict = {}
    t = _sys_trouble(1, 0, "Bus Receiver Failure")
    assert apply_alarm_to_trouble_store(store, t) is True
    assert apply_alarm_to_trouble_store(store, t) is False
    assert len(store) == 1
