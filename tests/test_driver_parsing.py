from keysight_u1242c import KeysightU1242C
from .fakes import REAL_TRACE_RESPONSES, response_factory


def test_driver_supports_different_command_orders():
    dmm = KeysightU1242C(
        port="COM16",
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    assert dmm.measure().value == 23.74
    assert dmm.identify().model == "U1242C"
    assert dmm.get_battery_percent() == 93.0
    assert dmm.get_status().normalized == "000000000900L00700000"
