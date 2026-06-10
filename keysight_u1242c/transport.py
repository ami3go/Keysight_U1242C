"""Serial transport layer for the Keysight U1242C driver."""

from __future__ import annotations

import logging
from typing import Any, Callable

from .exceptions import CommunicationError, InstrumentConnectionError, ResponseTimeoutError
from .parsers import normalize_response

SerialFactory = Callable[..., Any]


class SerialTransport:
    """Small wrapper around pyserial with deterministic line handling.

    Commands are transmitted with ``\r\n`` and responses are read as one line.
    The class intentionally contains no high-level instrument knowledge.
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 2.0,
        write_timeout: float = 2.0,
        encoding: str = "ascii",
        validate_port_exists: bool = True,
        logger: logging.Logger | None = None,
        serial_factory: SerialFactory | None = None,
        list_ports_provider: Callable[[], list[str]] | None = None,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.encoding = encoding
        self.validate_port_exists = validate_port_exists
        self.logger = logger or logging.getLogger(__name__)
        self._serial_factory = serial_factory
        self._list_ports_provider = list_ports_provider
        self._serial: Any | None = None

    @property
    def serial(self) -> Any | None:
        """Return the underlying serial object, mainly for tests/debugging."""

        return self._serial

    def available_ports(self) -> list[str]:
        """Return available serial port names when enumeration is possible."""

        if self._list_ports_provider is not None:
            return list(self._list_ports_provider())
        try:
            import serial.tools.list_ports  # type: ignore[import-not-found]
        except Exception:
            return []
        return [port.device for port in serial.tools.list_ports.comports()]

    def open(self) -> None:
        """Open the configured serial port."""

        if self.is_open():
            return

        if self.validate_port_exists:
            ports = self.available_ports()
            if ports and self.port not in ports:
                raise InstrumentConnectionError(
                    f"Serial port {self.port!r} not found. Available ports: {ports}"
                )

        try:
            if self._serial_factory is not None:
                self._serial = self._serial_factory(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    write_timeout=self.write_timeout,
                )
            else:
                try:
                    import serial  # type: ignore[import-not-found]
                except Exception as exc:
                    raise InstrumentConnectionError(
                        "pyserial is required to use real serial hardware. "
                        "Install the package with `pip install keysight-u1242c`."
                    ) from exc
                self._serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    write_timeout=self.write_timeout,
                )
        except InstrumentConnectionError:
            raise
        except Exception as exc:
            raise InstrumentConnectionError(f"Could not open serial port {self.port!r}: {exc}") from exc

        if not self.is_open():
            try:
                self._serial.open()
            except Exception as exc:
                raise InstrumentConnectionError(
                    f"Could not open serial port {self.port!r}: {exc}"
                ) from exc

    def close(self) -> None:
        """Close the serial port. Safe to call repeatedly."""

        serial_obj = self._serial
        self._serial = None
        if serial_obj is None:
            return
        try:
            is_open = getattr(serial_obj, "is_open", None)
            if is_open is None and hasattr(serial_obj, "isOpen"):
                attr = getattr(serial_obj, "isOpen")
                is_open = attr() if callable(attr) else bool(attr)
            if is_open or is_open is None:
                serial_obj.close()
        except Exception as exc:
            self.logger.debug("Ignoring serial close error on %s: %s", self.port, exc)

    def is_open(self) -> bool:
        """Return True when the serial object exists and reports open state."""

        serial_obj = self._serial
        if serial_obj is None:
            return False
        is_open = getattr(serial_obj, "is_open", None)
        if is_open is None and hasattr(serial_obj, "isOpen"):
            attr = getattr(serial_obj, "isOpen")
            is_open = attr() if callable(attr) else bool(attr)
        return bool(is_open)

    def write_line(self, command: str) -> None:
        """Write one command line using CRLF terminator."""

        if not self.is_open():
            raise InstrumentConnectionError(f"Serial port {self.port!r} is not open")
        data = f"{command}\r\n".encode(self.encoding)
        try:
            written = self._serial.write(data)
            if written is not None and written < len(data):
                raise CommunicationError(
                    f"Short serial write on {self.port!r}: wrote {written} of {len(data)} bytes"
                )
        except CommunicationError:
            raise
        except Exception as exc:
            raise CommunicationError(f"Serial write failed for {command!r}: {exc}") from exc

    def read_line(self) -> str:
        """Read and normalize one response line."""

        if not self.is_open():
            raise InstrumentConnectionError(f"Serial port {self.port!r} is not open")
        try:
            raw = self._serial.readline()
        except Exception as exc:
            raise CommunicationError(f"Serial read failed on {self.port!r}: {exc}") from exc

        response = normalize_response(raw, encoding=self.encoding)
        if response == "":
            raise ResponseTimeoutError(f"No response from instrument on {self.port!r}")
        return response

    def query(self, command: str) -> str:
        """Write a command and read one response line."""

        if not self.is_open():
            raise InstrumentConnectionError(f"Serial port {self.port!r} is not open")
        try:
            if hasattr(self._serial, "reset_input_buffer"):
                self._serial.reset_input_buffer()
        except Exception as exc:
            self.logger.debug("Ignoring reset_input_buffer error on %s: %s", self.port, exc)
        self.write_line(command)
        return self.read_line()
