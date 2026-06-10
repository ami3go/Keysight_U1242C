"""High-level production-oriented driver for the Keysight U1242C DMM."""

from __future__ import annotations

import csv
import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from . import commands
from .exceptions import (
    CommunicationError,
    InstrumentConnectionError,
    InvalidResponseError,
    KeysightU1242CError,
    ResponseTimeoutError,
)
from .parsers import (
    parse_battery_percent,
    parse_configuration,
    parse_identity,
    parse_measurement,
    parse_status,
)
from .transport import SerialTransport
from .types import Configuration, Identity, Measurement, Status

CsvErrorPolicy = Literal["keep_row", "skip_row", "stop"]

CSV_COLUMNS = [
    "timestamp_iso",
    "unix_time_s",
    "elapsed_s",
    "measurement_value",
    "unit",
    "function",
    "config_raw",
    "status_raw",
    "battery_percent",
    "measurement_raw",
    "error",
]


class KeysightU1242C:
    """Driver for the Keysight/Agilent U1242C handheld digital multimeter.

    The driver uses the observed line-based serial command protocol and is
    designed for long-running test benches with retries, reconnect, typed parsers,
    CSV logging, and idempotent cleanup.
    """

    def __init__(
        self,
        port: str | None = None,
        baudrate: int = 9600,
        timeout: float = 2.0,
        write_timeout: float = 2.0,
        retries: int = 2,
        retry_delay: float = 0.2,
        auto_reconnect: bool = True,
        strict_parsing: bool = False,
        battery_low_warning_percent: float = 30.0,
        battery_critical_warning_percent: float = 15.0,
        validate_port_exists: bool = True,
        encoding: str = "ascii",
        logger: logging.Logger | None = None,
        retry_side_effect_commands: bool = False,
        serial_factory: Any | None = None,
        list_ports_provider: Any | None = None,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.retries = max(0, retries)
        self.retry_delay = retry_delay
        self.auto_reconnect = auto_reconnect
        self.strict_parsing = strict_parsing
        self.battery_low_warning_percent = battery_low_warning_percent
        self.battery_critical_warning_percent = battery_critical_warning_percent
        self.validate_port_exists = validate_port_exists
        self.encoding = encoding
        self.logger = logger or logging.getLogger(__name__)
        self.retry_side_effect_commands = retry_side_effect_commands
        self._serial_factory = serial_factory
        self._list_ports_provider = list_ports_provider
        self._lock = threading.RLock()
        self._transport: SerialTransport | None = None
        self._last_config: Configuration | None = None
        self._last_identity: Identity | None = None

    def __enter__(self) -> "KeysightU1242C":
        self.connect()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    @property
    def transport(self) -> SerialTransport | None:
        """Return the current transport for diagnostics/tests."""

        return self._transport

    def connect(self, port: str | None = None) -> bool:
        """Open the serial port and verify the instrument identity."""

        with self._lock:
            if port is not None:
                self.port = port
            if not self.port:
                raise InstrumentConnectionError("No serial port configured")

            self.close()
            self._transport = SerialTransport(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
                encoding=self.encoding,
                validate_port_exists=self.validate_port_exists,
                logger=self.logger,
                serial_factory=self._serial_factory,
                list_ports_provider=self._list_ports_provider,
            )
            self._transport.open()
            idn_raw = self._query_current_transport_for_connect(commands.IDN)
            self._last_identity = parse_identity(idn_raw, strict=False)
            self.logger.info("Connected to Keysight U1242C on %s: %s", self.port, idn_raw)

            try:
                self.get_status_raw()
                self._last_config = self.get_configuration()
                battery = self.get_battery_percent()
                self._log_battery_warning(battery)
            except KeysightU1242CError as exc:
                self.logger.warning("Connected, but startup status query failed: %s", exc)
            return True


    def _query_current_transport_for_connect(self, command: str) -> str:
        """Query during connect without recursively invoking auto-reconnect."""

        if self._transport is None:
            raise InstrumentConnectionError("No serial transport available during connect")
        last_error: Exception | None = None
        attempts = self.retries + 1
        for attempt in range(1, attempts + 1):
            try:
                return self._transport.query(command)
            except (CommunicationError, InstrumentConnectionError) as exc:
                last_error = exc
                self.logger.warning(
                    "Startup query %s failed on attempt %s/%s: %s",
                    command,
                    attempt,
                    attempts,
                    exc,
                )
                if attempt < attempts:
                    time.sleep(self.retry_delay)
        if isinstance(last_error, KeysightU1242CError):
            raise last_error
        raise CommunicationError(f"Startup query {command!r} failed") from last_error

    def close(self) -> None:
        """Close the serial port. Safe to call multiple times."""

        with self._lock:
            if self._transport is not None:
                self._transport.close()
            self._transport = None

    def is_connected(self) -> bool:
        """Return True when the transport exists and is open."""

        return self._transport is not None and self._transport.is_open()

    def _ensure_connected(self) -> None:
        if not self.is_connected():
            if self.auto_reconnect and self.port:
                self.logger.info("Instrument not connected; attempting reconnect")
                self.connect(self.port)
                return
            raise InstrumentConnectionError("Instrument is not connected")

    def _reconnect_after_failure(self) -> None:
        if not self.auto_reconnect or not self.port:
            return
        self.logger.warning("Attempting reconnect to %s after communication failure", self.port)
        try:
            self.connect(self.port)
        except KeysightU1242CError as exc:
            self.logger.warning("Reconnect attempt failed: %s", exc)

    def query(self, command: str) -> str:
        """Send a query command and return the normalized one-line response."""

        last_error: Exception | None = None
        attempts = self.retries + 1
        for attempt in range(1, attempts + 1):
            with self._lock:
                try:
                    self._ensure_connected()
                    if self._transport is None:
                        raise InstrumentConnectionError("No serial transport available")
                    response = self._transport.query(command)
                    if response == "":
                        raise ResponseTimeoutError(f"Empty response for {command!r}")
                    return response
                except (CommunicationError, InstrumentConnectionError) as exc:
                    last_error = exc
                    self.logger.warning(
                        "Query %s failed on attempt %s/%s: %s",
                        command,
                        attempt,
                        attempts,
                        exc,
                    )
                    if attempt < attempts:
                        self._reconnect_after_failure()
            if attempt < attempts:
                time.sleep(self.retry_delay)

        if isinstance(last_error, KeysightU1242CError):
            raise last_error
        raise CommunicationError(f"Query {command!r} failed") from last_error

    def send(self, command: str, *, side_effect: bool = False) -> None:
        """Send a non-query command.

        Side-effect commands are not retried by default to avoid repeated reset,
        beep, or backlight changes after ambiguous write failures.
        """

        attempts = self.retries + 1 if (not side_effect or self.retry_side_effect_commands) else 1
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            with self._lock:
                try:
                    self._ensure_connected()
                    if self._transport is None:
                        raise InstrumentConnectionError("No serial transport available")
                    self._transport.write_line(command)
                    return
                except (CommunicationError, InstrumentConnectionError) as exc:
                    last_error = exc
                    self.logger.warning(
                        "Send %s failed on attempt %s/%s: %s", command, attempt, attempts, exc
                    )
                    if attempt < attempts and not side_effect:
                        self._reconnect_after_failure()
            if attempt < attempts:
                time.sleep(self.retry_delay)

        if isinstance(last_error, KeysightU1242CError):
            raise last_error
        raise CommunicationError(f"Send {command!r} failed") from last_error

    def identify_raw(self) -> str:
        """Return raw `*IDN?` response."""

        return self.query(commands.IDN)

    def identify(self) -> Identity:
        """Return parsed identity information."""

        identity = parse_identity(self.identify_raw(), strict=self.strict_parsing)
        self._last_identity = identity
        return identity

    def get_status_raw(self) -> str:
        """Return raw `STAT?` response."""

        return self.query(commands.STATUS)

    def get_status(self) -> Status:
        """Return parsed status. Meaning is preserved as raw/normalized text."""

        return parse_status(self.get_status_raw(), strict=self.strict_parsing)

    def get_configuration_raw(self) -> str:
        """Return raw `CONF?` response."""

        return self.query(commands.CONFIGURATION)

    def get_configuration(self) -> Configuration:
        """Return parsed `CONF?` configuration."""

        config = parse_configuration(self.get_configuration_raw(), strict=self.strict_parsing)
        self._last_config = config
        return config

    def get_battery_raw(self) -> str:
        """Return raw `SYST:BATT?` response."""

        return self.query(commands.BATTERY)

    def get_battery_percent(self) -> float | None:
        """Return parsed battery percentage, or None in tolerant mode."""

        battery = parse_battery_percent(self.get_battery_raw(), strict=self.strict_parsing)
        self._log_battery_warning(battery)
        return battery

    def measure_raw(self) -> str:
        """Return raw `FETC?` response."""

        return self.query(commands.FETCH)

    def measure(self, *, refresh_config: bool = False) -> Measurement:
        """Return parsed measurement.

        If the fetch response is numeric-only, function/unit are derived from the
        cached or freshly queried configuration.
        """

        config = self._last_config
        if refresh_config or config is None:
            try:
                config = self.get_configuration()
            except KeysightU1242CError as exc:
                self.logger.warning("Could not refresh configuration before measurement: %s", exc)
                config = self._last_config
        raw = self.measure_raw()
        return parse_measurement(raw, config=config, strict=self.strict_parsing)

    def reset(self) -> None:
        """Send instrument reset command."""

        self.send(commands.RESET, side_effect=True)

    def beep(self) -> None:
        """Trigger instrument beep."""

        self.send(commands.BEEP, side_effect=True)

    def set_backlight(self, enabled: bool) -> None:
        """Set backlight state."""

        self.send(commands.BACKLIGHT_ON if enabled else commands.BACKLIGHT_OFF, side_effect=True)

    def _log_battery_warning(self, battery: float | None) -> None:
        if battery is None:
            return
        if battery <= self.battery_critical_warning_percent:
            self.logger.critical("U1242C battery is critically low: %.1f%%", battery)
        elif battery <= self.battery_low_warning_percent:
            self.logger.warning("U1242C battery is low: %.1f%%", battery)

    # Backward-compatible aliases from the prototype.
    def init(self, com_port: str, baudrate_var: int = 9600) -> bool:
        """Deprecated compatibility alias for `connect()`."""

        self.baudrate = baudrate_var
        return self.connect(com_port)

    def get_data(self) -> str:
        """Deprecated compatibility alias for `measure_raw()`."""

        return self.measure_raw()

    def get_conf(self) -> str:
        """Deprecated compatibility alias for `get_configuration_raw()`."""

        return self.get_configuration_raw()

    def get_battery(self) -> str:
        """Deprecated compatibility alias for `get_battery_raw()`."""

        return self.get_battery_raw()

    def back_light(self, on_off: int | bool) -> None:
        """Deprecated compatibility alias for `set_backlight()`."""

        self.set_backlight(bool(on_off))

    def log_measurements_csv(
        self,
        output_path: str | Path,
        interval_s: float = 1.0,
        duration_s: float | None = None,
        append: bool = False,
        stop_event: threading.Event | None = None,
        error_policy: CsvErrorPolicy = "keep_row",
        include_status: bool = True,
        include_battery: bool = True,
        config_refresh_s: float | None = 60.0,
        status_refresh_s: float | None = 10.0,
        battery_refresh_s: float | None = 300.0,
        flush: bool = True,
        max_samples: int | None = None,
    ) -> int:
        """Log measurements to a CSV file at a defined interval.

        The generated CSV is readable by Excel, LibreOffice Calc, and
        `pandas.read_csv()` using default comma-separated parsing.
        """

        if interval_s <= 0:
            raise ValueError("interval_s must be > 0")
        if error_policy not in {"keep_row", "skip_row", "stop"}:
            raise ValueError("error_policy must be 'keep_row', 'skip_row', or 'stop'")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        file_exists = output.exists() and output.stat().st_size > 0
        mode = "a" if append else "w"

        start_monotonic = time.monotonic()
        next_sample_time = start_monotonic
        written = 0
        sample_index = 0
        last_config: Configuration | None = self._last_config
        last_status: Status | None = None
        last_battery: float | None = None
        last_config_refresh = None
        last_status_refresh = None
        last_battery_refresh = None

        def due(last_refresh: float | None, refresh_s: float | None, now_mono: float) -> bool:
            if last_refresh is None:
                return True
            if refresh_s is None:
                return False
            if refresh_s == 0:
                return True
            return now_mono - last_refresh >= refresh_s

        with output.open(mode, newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
            if not append or not file_exists:
                writer.writeheader()
                if flush:
                    fh.flush()

            while True:
                if stop_event is not None and stop_event.is_set():
                    break
                if max_samples is not None and sample_index >= max_samples:
                    break
                now_mono = time.monotonic()
                if duration_s is not None and now_mono - start_monotonic >= duration_s:
                    break

                sleep_s = next_sample_time - now_mono
                if sleep_s > 0:
                    if stop_event is None:
                        time.sleep(sleep_s)
                    else:
                        if stop_event.wait(timeout=sleep_s):
                            break
                elif -sleep_s > max(interval_s, 0.001):
                    self.logger.warning("CSV logger is behind schedule by %.3f s", -sleep_s)

                sample_mono = time.monotonic()
                unix_time = time.time()
                timestamp_iso = datetime.now().astimezone().isoformat(timespec="milliseconds")
                elapsed = sample_mono - start_monotonic
                error_parts: list[str] = []
                measurement: Measurement | None = None

                try:
                    if due(last_config_refresh, config_refresh_s, sample_mono):
                        try:
                            last_config = self.get_configuration()
                            last_config_refresh = sample_mono
                        except Exception as exc:  # keep logging when possible
                            error_parts.append(f"config: {exc}")
                    if include_status and due(last_status_refresh, status_refresh_s, sample_mono):
                        try:
                            last_status = self.get_status()
                            last_status_refresh = sample_mono
                        except Exception as exc:
                            error_parts.append(f"status: {exc}")
                    if include_battery and due(last_battery_refresh, battery_refresh_s, sample_mono):
                        try:
                            last_battery = self.get_battery_percent()
                            last_battery_refresh = sample_mono
                        except Exception as exc:
                            error_parts.append(f"battery: {exc}")

                    raw = self.measure_raw()
                    measurement = parse_measurement(raw, config=last_config, strict=self.strict_parsing)
                except Exception as exc:
                    error_parts.append(str(exc))
                    if error_policy == "stop":
                        raise
                    if error_policy == "skip_row":
                        sample_index += 1
                        next_sample_time += interval_s
                        continue

                row = {
                    "timestamp_iso": timestamp_iso,
                    "unix_time_s": f"{unix_time:.6f}",
                    "elapsed_s": f"{elapsed:.6f}",
                    "measurement_value": "" if measurement is None or measurement.value is None else measurement.value,
                    "unit": "" if measurement is None or measurement.unit is None else measurement.unit,
                    "function": "" if measurement is None or measurement.function is None else measurement.function,
                    "config_raw": "" if last_config is None else last_config.raw,
                    "status_raw": "" if last_status is None else last_status.normalized,
                    "battery_percent": "" if last_battery is None else last_battery,
                    "measurement_raw": "" if measurement is None else measurement.raw,
                    "error": "; ".join(error_parts),
                }
                writer.writerow(row)
                written += 1
                sample_index += 1
                if flush:
                    fh.flush()
                next_sample_time += interval_s
        return written


u1242c = KeysightU1242C
