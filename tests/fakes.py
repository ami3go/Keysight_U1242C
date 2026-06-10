from __future__ import annotations

from collections import defaultdict, deque


class FakeSerial:
    """Tiny pyserial-compatible fake for unit tests."""

    instances: list["FakeSerial"] = []
    fail_writes: int = 0
    fail_reads: int = 0

    def __init__(self, responses=None, port="COM16", **kwargs):
        self.port = port
        self.kwargs = kwargs
        self.is_open = True
        self.writes: list[bytes] = []
        self.reset_count = 0
        self.responses = responses if responses is not None else {}
        self.command_counts = defaultdict(int)
        FakeSerial.instances.append(self)

    def reset_input_buffer(self):
        self.reset_count += 1

    def write(self, data: bytes):
        if FakeSerial.fail_writes > 0:
            FakeSerial.fail_writes -= 1
            raise OSError("write failed")
        self.writes.append(data)
        return len(data)

    def readline(self):
        if FakeSerial.fail_reads > 0:
            FakeSerial.fail_reads -= 1
            raise OSError("read failed")
        if not self.writes:
            return b""
        command = self.writes[-1].decode("ascii").strip()
        self.command_counts[command] += 1
        if isinstance(self.responses, list):
            if not self.responses:
                return b""
            response = self.responses.pop(0)
        else:
            response = self.responses.get(command, "")
            if isinstance(response, deque):
                response = response.popleft() if response else ""
            elif isinstance(response, list):
                response = response.pop(0) if response else ""
            elif callable(response):
                response = response(command, self.command_counts[command])
        if isinstance(response, Exception):
            raise response
        if isinstance(response, bytes):
            return response
        return f"{response}\r\n".encode("ascii")

    def close(self):
        self.is_open = False

    def open(self):
        self.is_open = True


def response_factory(responses):
    def factory(**kwargs):
        return FakeSerial(responses=responses.copy() if isinstance(responses, dict) else list(responses), **kwargs)

    return factory


REAL_TRACE_RESPONSES = {
    "*IDN?": "Keysight Technologies,U1242C,MY57430015,V1.27",
    "STAT?": '"000000000900L00700000"',
    "CONF?": '"TEMP:K CEL"',
    "SYST:BATT?": "93%",
    "FETC?": "+2.37400000E+01",
}
