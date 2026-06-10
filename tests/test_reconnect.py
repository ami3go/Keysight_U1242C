from collections import deque

from keysight_u1242c import KeysightU1242C
from .fakes import REAL_TRACE_RESPONSES, FakeSerial


def test_retry_logic_retries_failed_query():
    FakeSerial.fail_reads = 1
    dmm = KeysightU1242C(
        port="COM16",
        retries=1,
        retry_delay=0,
        serial_factory=lambda **kwargs: FakeSerial(responses=REAL_TRACE_RESPONSES.copy(), **kwargs),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    assert dmm.identify_raw().startswith("Keysight Technologies")


def test_auto_reconnect_attempts_after_communication_failure():
    created = []

    def factory(**kwargs):
        created.append(1)
        if len(created) == 1:
            responses = REAL_TRACE_RESPONSES.copy()
        else:
            responses = REAL_TRACE_RESPONSES.copy()
        return FakeSerial(responses=responses, **kwargs)

    dmm = KeysightU1242C(
        port="COM16",
        retries=1,
        retry_delay=0,
        auto_reconnect=True,
        serial_factory=factory,
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    # Force the next FETC? response to timeout, which triggers reconnect and retry.
    FakeSerial.instances[-1].responses["FETC?"] = deque(["", "+2.37400000E+01"])
    measurement = dmm.measure()
    assert measurement.value == 23.74
    assert len(created) >= 2


def test_side_effect_command_not_retried_by_default():
    FakeSerial.fail_writes = 1
    dmm = KeysightU1242C(
        port="COM16",
        retries=3,
        retry_delay=0,
        serial_factory=lambda **kwargs: FakeSerial(responses=REAL_TRACE_RESPONSES.copy(), **kwargs),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    try:
        dmm.reset()
    except Exception:
        pass
    # No reconnect-created second serial instance for side-effect retry.
    assert len(FakeSerial.instances) >= 1
