import logging

import pytest

from keysight_u1242c import KeysightU1242C
from keysight_u1242c.exceptions import InstrumentConnectionError
from .fakes import REAL_TRACE_RESPONSES, response_factory


def test_successful_connection():
    dmm = KeysightU1242C(
        port="COM16",
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    assert dmm.connect() is True
    assert dmm.is_connected()
    dmm.close()
    assert not dmm.is_connected()


def test_com_port_not_found():
    dmm = KeysightU1242C(
        port="COM99",
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    with pytest.raises(InstrumentConnectionError):
        dmm.connect()


def test_validate_port_can_be_disabled():
    dmm = KeysightU1242C(
        port="COM99",
        validate_port_exists=False,
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    assert dmm.connect()


def test_battery_warning_threshold_logging(caplog):
    responses = REAL_TRACE_RESPONSES | {"SYST:BATT?": "14%"}
    dmm = KeysightU1242C(
        port="COM16",
        serial_factory=response_factory(responses),
        list_ports_provider=lambda: ["COM16"],
    )
    with caplog.at_level(logging.CRITICAL):
        dmm.connect()
    assert "critically low" in caplog.text
