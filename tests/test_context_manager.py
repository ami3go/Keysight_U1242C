from keysight_u1242c import KeysightU1242C
from .fakes import REAL_TRACE_RESPONSES, response_factory


def test_context_manager_opens_and_closes():
    dmm = KeysightU1242C(
        port="COM16",
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    with dmm as inst:
        assert inst.is_connected()
    assert not dmm.is_connected()


def test_close_idempotent():
    dmm = KeysightU1242C()
    dmm.close()
    dmm.close()
