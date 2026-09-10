"""Driver for the Keysight U1242C handheld multimeter.

Talks SCPI over the instrument's USB-serial interface, built on
scpi-driver-core (https://github.com/ami3go/scpi-driver-core) for the
transport, framing, and session lifecycle. This module only adds the
U1242C-specific commands.
"""

from __future__ import annotations

import time

from scpi_driver_core import ScpiClient, ScpiSession
from scpi_driver_core.scpi import ScpiTextCodec
from scpi_driver_core.transport import SerialTransport

__all__ = ["U1242C"]

_LOW_BATTERY_PERCENT = 30.0
_CRITICAL_BATTERY_PERCENT = 15.0


class U1242C:
    """Driver for the Keysight U1242C, over its USB-serial SCPI interface.

    Args:
        port: serial device, e.g. ``"COM16"`` or ``"/dev/ttyUSB0"``.
        baudrate: matches the instrument's USB-serial setting; 9600 by default.
        timeout_s: bound for each read/write on the connection.
    """

    def __init__(self, port: str, *, baudrate: int = 9600, timeout_s: float = 2.0) -> None:
        transport = SerialTransport(port, baudrate=baudrate, timeout_s=timeout_s)
        # The instrument answers with bare "\n"-terminated lines but tolerates
        # (and the original driver always sent) a "\r\n" command terminator.
        codec = ScpiTextCodec(command_terminator=b"\r\n", response_terminator=b"\n")
        self.session = ScpiSession("u1242c", ScpiClient(transport, codec=codec))

    def __enter__(self) -> "U1242C":
        self.init()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def init(self) -> None:
        """Open the connection, confirm the instrument responds, and report its state.

        Raises:
            ScpiDriverError: if the port cannot be opened or the instrument
                does not answer ``*IDN?``.
        """
        self.session.open()
        # get_identity() both confirms the instrument answers and caches its *IDN?.
        identity = self.session.get_identity()
        conf = self.get_conf()
        battery = self.get_battery_percent()
        print(f"Connected to: {identity.raw}, configured as {conf}, battery: {battery:.0f}%")

        if battery <= _CRITICAL_BATTERY_PERCENT:
            print(f"!!! WARNING !!! VERY LOW BATTERY {battery:.0f}% !!!")
            time.sleep(30)
        elif battery <= _LOW_BATTERY_PERCENT:
            print(f"!!! WARNING !!! LOW BATTERY {battery:.0f}% !!!")
            time.sleep(5)

    def close(self) -> None:
        self.session.close()

    # -- measurement --------------------------------------------------

    def get_data(self) -> float:
        """FETC?: the current primary measurement."""
        return self.session.client.query_float("FETC?")

    def get_conf(self) -> str:
        """CONF?: the active measurement configuration."""
        return self.session.client.query("CONF?")

    def get_battery_percent(self) -> float:
        """SYST:BATT?: remaining battery charge, as a percentage."""
        reading = self.session.client.query("SYST:BATT?")
        return float(reading.replace("%", "").strip())

    def reset(self) -> None:
        """*RST: return the instrument to its power-on default state."""
        self.session.client.write("*RST")

    def beep(self) -> None:
        """SYST:BEEP: sound the instrument's beeper once."""
        self.session.client.write("SYST:BEEP")

    def back_light(self, on: bool) -> None:
        """SYST:BLIT: turn the display backlight on or off."""
        self.session.client.write(f"SYST:BLIT {1 if on else 0}")
