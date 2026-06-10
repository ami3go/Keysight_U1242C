import pytest

from keysight_u1242c import KeysightU1242C
from keysight_u1242c.exceptions import ResponseTimeoutError
from .fakes import REAL_TRACE_RESPONSES, FakeSerial, response_factory


def connected_dmm(responses=None):
    dmm = KeysightU1242C(
        port="COM16",
        serial_factory=response_factory(responses or REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    return dmm


def test_idn_query_success():
    dmm = connected_dmm()
    assert "Keysight Technologies" in dmm.identify_raw()


def test_measure_raw_returns_raw_response():
    dmm = connected_dmm()
    assert dmm.measure_raw() == "+2.37400000E+01"


def test_measure_parses_numeric_and_config():
    dmm = connected_dmm()
    measurement = dmm.measure()
    assert measurement.value == pytest.approx(23.74)
    assert measurement.unit == "CEL"


def test_empty_response_timeout():
    responses = REAL_TRACE_RESPONSES | {"FETC?": ""}
    dmm = KeysightU1242C(
        port="COM16",
        retries=0,
        serial_factory=response_factory(responses),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    with pytest.raises(ResponseTimeoutError):
        dmm.measure_raw()


def test_stat_returns_raw_status():
    dmm = connected_dmm()
    assert dmm.get_status_raw() == '"000000000900L00700000"'
    assert dmm.get_status().normalized == "000000000900L00700000"


def test_backward_compatible_aliases():
    dmm = KeysightU1242C(
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    assert dmm.init("COM16") is True
    assert dmm.get_data() == "+2.37400000E+01"
    assert dmm.get_conf() == '"TEMP:K CEL"'
    assert dmm.get_battery() == "93%"
    dmm.back_light(1)
    assert FakeSerial.instances[-1].writes[-1] == b"SYST:BLIT 1\r\n"
