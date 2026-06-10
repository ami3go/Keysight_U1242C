import pytest

from keysight_u1242c.exceptions import ParseError
from keysight_u1242c.parsers import (
    normalize_response,
    parse_battery_percent,
    parse_configuration,
    parse_identity,
    parse_measurement,
    parse_status,
)


def test_normalize_response_strips_crlf():
    assert normalize_response(b"93%\r\n") == "93%"


def test_parse_identity_real_trace():
    idn = parse_identity("Keysight Technologies,U1242C,MY57430015,V1.27")
    assert idn.manufacturer == "Keysight Technologies"
    assert idn.model == "U1242C"
    assert idn.serial_number == "MY57430015"
    assert idn.firmware_version == "V1.27"


def test_parse_status_real_trace_preserves_raw_and_normalized():
    status = parse_status('"000000000900L00700000"')
    assert status.raw == '"000000000900L00700000"'
    assert status.normalized == "000000000900L00700000"


def test_parse_configuration_real_trace():
    conf = parse_configuration('"TEMP:K CEL"')
    assert conf.raw == '"TEMP:K CEL"'
    assert conf.function == "TEMP:K"
    assert conf.sensor == "K"
    assert conf.unit == "CEL"


def test_parse_battery_real_trace():
    assert parse_battery_percent("93%") == 93.0


def test_parse_battery_malformed_tolerant_and_strict():
    assert parse_battery_percent("bad", strict=False) is None
    with pytest.raises(ParseError):
        parse_battery_percent("bad", strict=True)


def test_parse_measurement_scientific_notation_with_config():
    conf = parse_configuration('"TEMP:K CEL"')
    measurement = parse_measurement("+2.37400000E+01", config=conf)
    assert measurement.value == pytest.approx(23.74)
    assert measurement.unit == "CEL"
    assert measurement.function == "TEMP:K"
