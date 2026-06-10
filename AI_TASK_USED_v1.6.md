# AI Task: Refactor Keysight U1242C Serial Driver for 24/7 Production Use

## Change History

| Version | Change |
|---|---|
| 1.0 | Initial production refactor task. |
| 1.1 | Added real-device trace requirements for `STAT?`, `CONF?`, `SYST:BATT?`, and `FETC?` behavior. |
| 1.2 | Added required examples, API documentation, and CSV measurement logging with timestamped interval sampling readable by Excel and pandas. |
| 1.3 | Added final production clarifications: safer exception names, extended constructor options, serial response normalization, side-effect retry policy, CSV logging overrun behavior, optional port validation, and hardware-free example tests. |
| 1.4 | Added GitHub repository Markdown file requirements, including README, CHANGELOG, CONTRIBUTING, SUPPORT, and release-ready repository documentation. |
| 1.5 | Added explicit requirement to generate the project as a Python installable module/package with `pyproject.toml`, runtime metadata, wheel/sdist build support, editable install support, and import/packaging tests. |
| 1.6 | Implemented final review fixes: corrected serial terminator Markdown, clarified retry policy for side-effect commands, added parser module, CLI entry point, CSV metadata refresh/caching, GitHub repo support files, optional hardware smoke test, and related acceptance criteria. |


## 1. Task Summary

Refactor the existing `keysight_U1242C_class.py` prototype into a production-grade Python driver for the Keysight/Agilent U1242C handheld digital multimeter.

The current implementation provides basic serial communication and a few commands, but it is not suitable for unattended 24/7 operation. The refactor shall improve reliability, diagnostics, error handling, reconnect behavior, testability, packaging, and API design while preserving the existing basic functionality.

Primary target use case:

- Long-running automated test systems.
- 24/7 measurement logging.
- Integration into larger Python test benches with multiple instruments.
- Stable operation on Windows with USB/serial adapter connected to the U1242C.

---

## 2. Current Code Problems to Fix

The existing class has the following production-readiness issues:

1. Class name `u1242c` does not follow Python production naming conventions.
2. Serial timeout is hardcoded to `0.1` seconds.
3. Serial operations have no exception handling.
4. No reconnect or recovery mechanism exists after USB/serial failure.
5. `_query()` returns raw strings without checking for empty, malformed, or partial responses.
6. Battery parsing can crash if the response is empty or unexpected.
7. `init()` uses blocking `time.sleep(5)` and `time.sleep(30)` for low-battery warnings.
8. Driver uses `print()` instead of structured logging.
9. No thread lock protects serial communication.
10. `close()` can fail if the port is already closed or `self.ser` is `None`.
11. `self.ser.isOpen` is not robust; modern pyserial uses `self.ser.is_open`.
12. Typographical errors exist in API and command names, for example `battely_level` and `black_light`.
13. There are no custom exceptions.
14. There are no unit tests.
15. There is no installable package structure.
16. The script contains direct `if __name__ == '__main__'` test code instead of proper examples/tests.

---

## 3. Refactor Goals

The AI agent shall convert the prototype into a robust driver with:

- Clean public API.
- Configurable serial parameters.
- Defensive communication handling.
- Reconnect and retry support.
- Typed return values where possible.
- Structured logging.
- Context manager support.
- Unit tests using mocked serial communication.
- Installable Python package layout.
- Backward-compatible aliases where reasonable.
- Clear documentation and examples.

Target production rating after refactor: **8/10 or higher** for 24/7 unattended use.

---

## 4. Required Package Structure

Create the following package structure:

```text
keysight_u1242c/
  pyproject.toml
  README.md
  CHANGELOG.md
  CONTRIBUTING.md
  SUPPORT.md
  src/
    keysight_u1242c/
      __init__.py
      driver.py
      commands.py
      exceptions.py
      parsers.py
      transport.py
      types.py
      cli.py
  examples/
    basic_measurement.py
    continuous_logging.py
    battery_check.py
    csv_measurement_logger.py
    reconnect_logging.py
    hardware_smoke_test.py
  docs/
    api.md
    logging.md
    production_notes.md
  .gitignore
  LICENSE
  tests/
    test_driver_connection.py
    test_driver_queries.py
    test_driver_parsing.py
    test_parsers.py
    test_cli.py
    test_reconnect.py
    test_context_manager.py
    test_csv_logging.py
    test_documentation_examples.py
    test_hardware_smoke_example.py
```

The package shall be installable using:

```bash
pip install -e .
```

### 4.1 Python Installable Module Requirements

The AI agent shall generate the final code as a proper Python installable module/package, not as a loose collection of scripts.

Required packaging behavior:

1. The repository root shall contain a valid `pyproject.toml`.
2. The package shall use a modern `src/` layout:

```text
src/
  keysight_u1242c/
    __init__.py
    driver.py
    commands.py
    exceptions.py
    parsers.py
    transport.py
    types.py
    cli.py
```

3. The distribution/package name shall be:

```text
keysight-u1242c
```

4. The import package name shall be:

```python
keysight_u1242c
```

5. After installation, this import shall work from any directory:

```python
from keysight_u1242c import KeysightU1242C
```

6. `src/keysight_u1242c/__init__.py` shall export at minimum:

```python
from .driver import KeysightU1242C
from .types import Measurement, Configuration, Status
from .exceptions import (
    KeysightU1242CError,
    InstrumentConnectionError,
    CommunicationError,
    ResponseTimeoutError,
    InvalidResponseError,
    ParseError,
)

__all__ = [
    "KeysightU1242C",
    "Measurement",
    "Configuration",
    "Status",
    "KeysightU1242CError",
    "InstrumentConnectionError",
    "CommunicationError",
    "ResponseTimeoutError",
    "InvalidResponseError",
    "ParseError",
]
```

7. The package shall define a version, preferably using one of these approaches:

```python
# src/keysight_u1242c/__init__.py
__version__ = "0.1.0"
```

or dynamic version metadata if the chosen build backend supports it.

8. Runtime dependencies shall be minimal. Required runtime dependency:

```text
pyserial
```

9. Test/development dependencies shall be optional extras, for example:

```bash
pip install -e .[dev]
```

The `dev` extra shall include at minimum:

```text
pytest
black
ruff
pandas
build
```

`pandas` shall remain a development/test dependency only unless a future feature explicitly requires it at runtime.

10. The package shall be buildable into wheel and source distribution:

```bash
python -m build
```

Expected generated artifacts:

```text
dist/keysight_u1242c-<version>-py3-none-any.whl
dist/keysight_u1242c-<version>.tar.gz
```

11. The generated package shall support these commands during validation:

```bash
python -m pip install -e .
python -c "from keysight_u1242c import KeysightU1242C; print(KeysightU1242C)"
python -m pytest
python -m build
```

12. The package metadata in `pyproject.toml` shall include at minimum:

- Project name.
- Version.
- Description.
- Python requirement, `>=3.10`.
- Runtime dependencies.
- Optional development dependencies.
- README reference.
- License field or license file reference.
- Author placeholder or neutral maintainer field.
- Classifiers suitable for a serial instrument driver.

13. Do not require users to modify `PYTHONPATH` manually. Correct packaging shall make the import work after install.

14. Example scripts shall import the installed package, not use relative imports from source files.

15. Tests shall verify package importability from the installed/editable package.

16. The package shall define an optional command-line entry point for CSV logging and hardware checks:

```toml
[project.scripts]
u1242c-log = "keysight_u1242c.cli:main"
```

The CLI shall support at minimum:

```bash
u1242c-log --port COM16 --interval 1.0 --output u1242c_log.csv
u1242c-log --port COM16 --once
u1242c-log --port COM16 --hardware-check
```

17. The repository shall contain Python project support files suitable for GitHub:

```text
.gitignore
LICENSE
```

The `LICENSE` may be a placeholder if the final license is not known, but it shall clearly instruct the maintainer to select a license before public release.

---

## 5. Public API Requirements

Implement a public class:

```python
class KeysightU1242C:
    ...
```

### 5.1 Constructor

```python
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
) -> None:
    ...
```

Constructor requirements:

- `strict_parsing=False` shall make parsers tolerant and return typed objects with `None` fields where possible.
- `strict_parsing=True` shall raise `ParseError` for malformed parseable-domain responses.
- `validate_port_exists=True` shall check available COM ports when enumeration is supported.
- `validate_port_exists=False` shall skip enumeration and try to open the provided port directly.
- `encoding` shall be used for serial response decoding. Default shall be `ascii`, because observed U1242C responses are ASCII text.
- Battery warning thresholds shall be configurable and shall not cause blocking sleeps.

### 5.2 Required Public Methods

Implement at minimum:

```python
connect(port: str | None = None) -> None
close() -> None
is_connected() -> bool
identify() -> str
get_status_raw() -> str
get_status() -> Status
measure_raw() -> str
measure() -> Measurement
get_config() -> str
get_configuration() -> Configuration
get_battery_percent() -> float | None
reset() -> None
beep() -> None
set_backlight(enabled: bool) -> None
query(command: str) -> str
send(command: str) -> None
log_measurements_csv(
    path: str | pathlib.Path,
    interval_s: float,
    duration_s: float | None = None,
    append: bool = True,
    include_header: bool = True,
    stop_event: threading.Event | None = None,
    error_policy: Literal["keep_row", "skip_row", "stop"] = "keep_row",
    include_status: bool = True,
    include_battery: bool = True,
    config_refresh_s: float | None = 60.0,
    status_refresh_s: float | None = 10.0,
    battery_refresh_s: float | None = 300.0,
) -> None
```

### 5.2.1 Measurement Logging API

The driver shall provide an easy high-level API for logging measurements to a CSV file at a defined time interval. The output shall be directly readable by Microsoft Excel, LibreOffice Calc, and `pandas.read_csv()`.

Required behavior for `log_measurements_csv(...)`:

- Create the target CSV file if it does not exist.
- Support appending to an existing CSV file.
- Write a header row by default.
- Use UTF-8 encoding.
- Use comma-separated CSV format.
- Use `newline=""` when opening the file to avoid blank lines on Windows.
- Include ISO-8601 timestamp with timezone or local offset where possible.
- Include Unix timestamp seconds for easy plotting and numerical analysis.
- Include elapsed time seconds from logging start.
- Include raw measurement response.
- Include parsed measurement value.
- Include unit, function, configuration raw string, status raw string, and battery percentage when available.
- Avoid unnecessary repeated metadata queries during long logging sessions. Configuration, status, and battery values may be cached and refreshed at configurable intervals using `config_refresh_s`, `status_refresh_s`, and `battery_refresh_s`.
- Support disabling optional metadata queries with `include_status=False` and/or `include_battery=False`.
- Continue logging after recoverable communication errors when retry/reconnect succeeds.
- Log communication errors using the package logger.
- Stop cleanly on `KeyboardInterrupt` and close/flush the file.
- Support `duration_s=None` for infinite logging until interrupted or until `stop_event` is set.
- Validate that `interval_s > 0`.
- Use monotonic time for interval scheduling to avoid drift from system clock adjustments.

Required CSV columns:

```text
timestamp_iso,unix_time_s,elapsed_s,measurement_value,unit,function,config_raw,status_raw,battery_percent,measurement_raw,error
```

Example CSV row:

```csv
2026-06-10T12:15:30.123+02:00,1781093730.123,0.000,23.74,CEL,TEMP:K,"TEMP:K CEL","000000000900L00700000",93.0,+2.37400000E+01,
```

The CSV file shall be readable with:

```python
import pandas as pd
df = pd.read_csv("u1242c_log.csv")
```

### 5.3 Context Manager Support

The driver shall support:

```python
from keysight_u1242c import KeysightU1242C

with KeysightU1242C(port="COM16") as dmm:
    print(dmm.identify())
    print(dmm.measure())
```

### 5.4 Backward-Compatible Aliases

For compatibility with existing scripts, optionally support deprecated aliases:

```python
init(com_port, baudrate_var=9600) -> bool
get_data() -> str
get_conf() -> str
get_battery() -> str
back_light(on_off) -> None
```

These aliases shall emit `DeprecationWarning` and call the new methods internally.

---

## 6. Serial Transport Requirements

Create a separate `SerialTransport` class in `transport.py`.

### 6.1 Responsibilities

The transport layer shall handle:

- Opening and closing the serial port.
- Writing commands with `\r\n` terminator.
- Reading one response line.
- Resetting input buffer before query.
- Configurable timeout and write timeout.
- Serial exception handling.
- Optional retry logic.
- Optional reconnect logic.
- Thread-safe access using `threading.RLock` or `threading.Lock`.

### 6.2 Required Transport Methods

```python
open() -> None
close() -> None
is_open() -> bool
write_line(text: str) -> None
query_line(text: str) -> str
reconnect() -> None
```

### 6.2.1 Serial Line and Encoding Rules

- Commands shall be transmitted with `\r\n` line terminator.
- Responses shall be decoded using the configured `encoding`, default `ascii`.
- Response parsing shall strip trailing `\r`, `\n`, and surrounding whitespace.
- Dataclass `raw` fields shall preserve the response content after serial line terminators are removed.
- The transport shall treat a decoded empty line as a timeout/empty-response condition, not as a valid measurement.
- The transport shall not mix responses between commands; protect complete write/read query transactions with the same lock.

### 6.3 Serial Exceptions

Catch pyserial exceptions and re-raise custom driver exceptions.

Handle at minimum:

```python
serial.SerialException
serial.SerialTimeoutException
OSError
UnicodeDecodeError
```

---

## 7. Custom Exceptions

Create `exceptions.py` with:

```python
class KeysightU1242CError(Exception):
    """Base exception for all Keysight U1242C driver errors."""

class InstrumentConnectionError(KeysightU1242CError):
    """Raised when the instrument cannot be connected or connection is lost."""

class CommunicationError(KeysightU1242CError):
    """Raised when serial communication fails."""

class ResponseTimeoutError(CommunicationError):
    """Raised when the instrument does not respond in time."""

class InvalidResponseError(CommunicationError):
    """Raised when the instrument response is empty or malformed."""

class ParseError(KeysightU1242CError):
    """Raised when a valid-looking response cannot be parsed."""
```

Do not name custom exceptions `ConnectionError`, because that shadows Python built-in `ConnectionError`. Use `InstrumentConnectionError` or another clearly namespaced name instead.

---

## 8. Commands Module

Create `commands.py` with command constants or an enum-like structure.

Required commands:

```python
IDN = "*IDN?"
STATUS = "STAT?"
FETCH = "FETC?"
CONFIGURATION = "CONF?"
BATTERY = "SYST:BATT?"
RESET = "*RST"
BEEP = "SYST:BEEP"
BACKLIGHT_ON = "SYST:BLIT 1"
BACKLIGHT_OFF = "SYST:BLIT 0"
```

Do not keep typo names such as `battely_level` or `black_light` in the new command layer.

### 8.1 Real-Device Trace-Based Commands

The following command/response pairs were observed from a real Keysight U1242C device and shall be treated as regression-test inputs:

| Command | Example response | Required handling |
|---|---|---|
| `*IDN?` | `Keysight Technologies,U1242C,MY57430015,V1.27` | Return non-empty identity string. |
| `STAT?` | `"000000000900L00700000"` | Add support and preserve raw status. |
| `CONF?` | `"TEMP:K CEL"` | Parse function/sensor/unit while preserving raw text. |
| `SYST:BATT?` | `93%` | Parse numeric percentage as `93.0`. |
| `FETC?` | `+2.37400000E+01` | Parse as float value `23.74`; derive unit from configuration if needed. |

The driver shall not require these commands to be called in a fixed order. The trace shows that valid communication may occur in different sequences, for example `*IDN?`, `STAT?`, `CONF?`, `SYST:BATT?`, `FETC?`, or `*IDN?`, `FETC?`, `STAT?`, `CONF?`, `SYST:BATT?`.

---

## 9. Measurement Type

Create `types.py` with a dataclass:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Measurement:
    raw: str
    value: float | None
    unit: str | None
    function: str | None = None
    config_raw: str | None = None

@dataclass(frozen=True)
class Configuration:
    raw: str
    function: str | None
    sensor: str | None
    unit: str | None

@dataclass(frozen=True)
class Status:
    raw: str
    normalized: str
```

`Status` shall preserve the raw status string until the official status bit mapping is available. Do not invent or hard-code undocumented status-bit meanings.

### 9.1 Measurement Parsing

Implement basic parser behavior:

- Always preserve the raw response.
- Support scientific notation responses such as `+2.37400000E+01`.
- Try to parse a numeric value from the response.
- Try to extract a unit when available.
- If the `FETC?` response contains only a number, derive function and unit from `CONF?` or cached `Configuration`.
- If parsing fails, return `Measurement(raw=response, value=None, unit=None)` unless strict mode is enabled.

Optional constructor parameter:

```python
strict_parsing: bool = False
```

If `strict_parsing=True`, malformed measurements shall raise `ParseError`.

### 9.2 Configuration Parsing

Implement:

```python
get_configuration() -> Configuration
```

The parser shall support at least the real trace response:

```text
"TEMP:K CEL"
```

Expected parsed result:

```python
Configuration(
    raw='"TEMP:K CEL"',
    function="TEMP",
    sensor="K",
    unit="CEL",
)
```

The parser shall strip surrounding quotes but preserve the original raw response. If the format is unknown, return a `Configuration` object with `raw` populated and unknown fields set to `None`, unless strict parsing is enabled.

### 9.3 Status Handling

Implement:

```python
get_status_raw() -> str
get_status() -> Status
```

The parser shall support at least the real trace response:

```text
"000000000900L00700000"
```

Expected basic result:

```python
Status(
    raw='"000000000900L00700000"',
    normalized="000000000900L00700000",
)
```

Do not decode individual status bits unless the official Keysight documentation is provided. The first production version shall only preserve and normalize the string.

---

## 9.4 Parser Module Requirements

Create `parsers.py` so parsing can be unit-tested independently from serial communication. The module shall contain pure helper functions with no hardware access:

```python
parse_measurement(raw: str, config: Configuration | None = None, strict: bool = False) -> Measurement
parse_configuration(raw: str, strict: bool = False) -> Configuration
parse_status(raw: str) -> Status
parse_battery_percent(raw: str, strict: bool = False) -> float | None
```

Parser requirements:

- Parser functions shall be deterministic and side-effect free.
- Parser functions shall not open serial ports, sleep, log excessively, or depend on global driver state.
- Unit tests shall cover parser behavior directly using real trace samples and malformed inputs.
- Driver methods may call these parser helpers instead of duplicating parsing logic in `driver.py`.

---

## 10. Battery Parsing Requirements

Implement:

```python
get_battery_percent() -> float | None
```

Requirements:

- Return `float` if a numeric battery percentage can be parsed.
- Return `None` if the response is valid but not numeric.
- Raise `InvalidResponseError` for empty response.
- Do not sleep inside the driver.
- Log warnings if battery is below warning thresholds.

Default thresholds:

```python
battery_low_warning_percent = 30.0
battery_critical_warning_percent = 15.0
```

The application, not the driver, shall decide whether to pause, stop, or continue.

---

## 11. Logging Requirements

Replace all `print()` calls with `logging`.

Log levels:

- `DEBUG`: sent commands and received responses.
- `INFO`: successful connection, disconnection, identified instrument.
- `WARNING`: low battery, retry attempts, reconnect attempts.
- `ERROR`: failed communication after retries.
- `EXCEPTION`: unexpected exceptions with traceback.

Do not log excessively during high-rate measurement loops unless debug logging is enabled.

---

## 12. CSV Measurement Logging Requirements

The package shall include a production-ready CSV measurement logger suitable for long-duration tests. This can be implemented either as a method on `KeysightU1242C`, as a helper class such as `CsvMeasurementLogger`, or both. The public API must remain easy for a user to start interval-based logging with minimal code.

### 12.1 Required CSV Logger Features

- User-defined measurement interval in seconds.
- Optional finite duration in seconds.
- Infinite logging mode until Ctrl+C or external stop event.
- Timestamp for every measurement.
- CSV format that opens cleanly in Excel and can be loaded directly by pandas.
- Robust file flushing to reduce data loss during long tests.
- Optional append mode for continuing an existing log file.
- Optional metadata comments are allowed only if they do not break `pandas.read_csv()` by default; prefer regular columns over commented metadata.
- Store errors in the `error` column instead of silently dropping failed samples.
- Configurable behavior for failed samples: keep row with error, skip row, or stop logging. Default shall be to keep a row with timestamp and error text.
- Do not use blocking sleeps that prevent clean shutdown; use interruptible loop logic where possible.

### 12.2 Required CSV Columns

The default CSV output shall contain these columns in this order:

```text
timestamp_iso,unix_time_s,elapsed_s,measurement_value,unit,function,config_raw,status_raw,battery_percent,measurement_raw,error
```

Column meaning:

| Column | Meaning |
|---|---|
| `timestamp_iso` | Human-readable ISO-8601 timestamp with local timezone/offset when possible. |
| `unix_time_s` | Floating-point Unix timestamp for pandas/matplotlib plotting. |
| `elapsed_s` | Seconds from start of logging, measured with monotonic clock. |
| `measurement_value` | Parsed numeric measurement value, empty if parse failed. |
| `unit` | Unit from parsed response or configuration, for example `CEL`. |
| `function` | Function/config context, for example `TEMP:K`. |
| `config_raw` | Raw `CONF?` response. |
| `status_raw` | Raw normalized `STAT?` response when available. |
| `battery_percent` | Parsed battery percentage when available. |
| `measurement_raw` | Raw `FETC?` response. |
| `error` | Empty on success; contains error message on failed sample. |

### 12.3 Required pandas and Excel Compatibility

The generated CSV shall be readable by pandas without custom parsing:

```python
import pandas as pd
df = pd.read_csv("u1242c_log.csv")
```

The generated CSV shall be easy to open in Excel. Use a normal header row and comma-separated values. Avoid multi-line cells and avoid comment headers by default.

`pandas` may be used as a test dependency only. The runtime package shall not require pandas for normal driver operation or CSV logging.

### 12.3.1 Interval Overrun Behavior

If one measurement cycle takes longer than `interval_s`, the logger shall:

- Write the sample as soon as possible.
- Not start overlapping measurement calls.
- Continue scheduling from a monotonic timeline to avoid long-term drift.
- Log a warning when the logger falls behind schedule.
- Preserve a timestamp for the actual sample time, not the scheduled time.


### 12.3.2 Metadata Refresh and Caching

The CSV logger shall avoid unnecessary repeated metadata queries, especially during long 24/7 logging sessions. The implementation shall support configurable refresh intervals for metadata that changes slowly:

```python
include_status: bool = True
include_battery: bool = True
config_refresh_s: float | None = 60.0
status_refresh_s: float | None = 10.0
battery_refresh_s: float | None = 300.0
```

Required behavior:

- `FETC?` shall normally be queried for every measurement sample.
- `CONF?` may be cached and refreshed according to `config_refresh_s`.
- `STAT?` may be cached and refreshed according to `status_refresh_s` when `include_status=True`.
- `SYST:BATT?` may be cached and refreshed according to `battery_refresh_s` when `include_battery=True`.
- A refresh interval of `None` means query once at logger start and reuse the cached value.
- A refresh interval of `0` means query on every sample.
- If a metadata refresh fails but the measurement succeeds, write the measurement row and put the metadata error in the `error` column according to `error_policy`.

### 12.4 Required Logging Example

Provide an example script that logs measurements every defined interval:

```bash
python examples/csv_measurement_logger.py --port COM16 --interval 1.0 --output u1242c_log.csv
```

The example shall support at minimum:

```text
--port COM16
--interval 1.0
--duration 3600
--output u1242c_log.csv
--append
```

---

## 13. Retry and Reconnect Requirements

### 13.1 Query Retry

For `query()` and non-side-effect `send()` operations:

- Try the operation once.
- If it fails, retry up to `retries` times.
- Sleep `retry_delay` between retries.
- If `auto_reconnect=True`, attempt reconnect after communication failure.
- If all attempts fail, raise `CommunicationError` or a more specific subclass.

Side-effect commands are governed by section 13.3 and shall not be blindly retried by default.

### 13.2 Empty Response Handling

If a query returns an empty string:

- Retry according to configured retry count.
- If still empty, raise `ResponseTimeoutError`.

### 13.3 Side-Effect Command Retry Policy

Queries such as `*IDN?`, `STAT?`, `CONF?`, `SYST:BATT?`, and `FETC?` may be retried automatically.

Side-effect commands such as `reset()`, `beep()`, and `set_backlight()` shall not be blindly retried after bytes may have been written to the serial port. The implementation shall use one of these safe policies:

1. Retry only failures that occur before any bytes are confirmed written; or
2. Provide an explicit option such as `retry_side_effect_commands`, default `False`.

The default behavior shall avoid repeated reset/backlight/beep side effects during ambiguous communication failures.

---

## 14. Thread Safety

All serial operations shall be protected with a lock.

Requirement:

```python
with self._lock:
    ... serial write/read ...
```

This prevents response mixing when the driver is called from GUI threads, logger threads, or automation workers.

---

## 15. Connection Lifecycle Requirements

### 15.1 Connect

`connect()` shall:

1. Validate that the requested port exists if port enumeration is available and `validate_port_exists=True`; if `validate_port_exists=False`, attempt to open the provided port directly.
2. Open the serial port.
3. Query `*IDN?`.
4. Verify that a non-empty ID string is returned.
5. Log connected instrument identity.
6. Optionally query `STAT?`, `CONF?`, and `SYST:BATT?`.
7. Do not block with long sleeps during startup; only log warnings or expose status to the application.

### 15.2 Close

`close()` shall be safe to call multiple times.

It shall not raise if:

- Driver was never connected.
- Port is already closed.
- `self.ser` is `None`.

### 15.3 Disconnection Detection

`is_connected()` shall return `False` if:

- No transport exists.
- Serial port is closed.
- Serial port object is invalid.

---

## 16. Backward Compatibility

The old class name may be preserved as a deprecated alias:

```python
u1242c = KeysightU1242C
```

This shall emit a warning in documentation. Do not make the new API depend on the old class name.

---

## 17. Testing Requirements

Use `pytest`.

Tests shall not require real hardware.

Mock or fake the serial object.

### 17.1 Required Tests

Implement tests for:

1. Successful connection.
2. COM port not found.
3. `*IDN?` query success.
4. Empty response timeout.
5. Malformed battery response.
6. Numeric battery response with `%` sign.
7. Battery warning threshold logging.
8. `measure_raw()` returns raw response.
9. `measure()` parses numeric value when possible.
10. `close()` is idempotent.
11. Context manager opens and closes correctly.
12. Serial exception converted to driver exception.
13. Retry logic retries failed query.
14. Auto-reconnect attempts after communication failure.
15. Deprecated compatibility methods still work.
16. `STAT?` returns raw status string and normalized status string.
17. `CONF?` parser handles `"TEMP:K CEL"`.
18. `FETC?` parser handles `+2.37400000E+01` as `23.74`.
19. `measure()` attaches function/unit from `CONF?` when `FETC?` is numeric only.
20. Regression tests use real trace samples for `*IDN?`, `STAT?`, `CONF?`, `SYST:BATT?`, and `FETC?`.
21. Driver supports different valid command orders and does not depend on a fixed sequence.
22. CSV measurement logger creates a valid CSV file with the required header.
23. CSV measurement logger writes timestamped rows at the configured interval.
24. CSV measurement logger output is readable by `pandas.read_csv()` in tests.
25. CSV logger writes error rows for failed samples according to default policy.
26. CSV logger supports append mode without duplicating the header unless requested.
27. CSV logger stops cleanly on duration expiry or external stop event.
28. Example scripts and documentation snippets can be syntax/import/CLI-tested without real hardware.
29. Hardware-dependent examples support `--help` and do not connect unless explicitly executed by the user.

### 17.2 Mock Serial Requirements

Create a fake serial class for tests that can simulate:

- Valid line responses.
- Empty responses.
- Exceptions during write.
- Exceptions during read.
- Port open/close state.
- Reconnect success/failure.
- Real trace command/response sequences loaded from fixture data.

---

## 18. Example Scripts

### 18.1 `examples/basic_measurement.py`

Demonstrate:

- Connect to COM port.
- Print IDN.
- Print raw status.
- Print parsed configuration.
- Print one measurement.
- Print battery percentage.
- Close cleanly.

### 18.2 `examples/continuous_logging.py`

Demonstrate:

- Continuous measurement loop.
- Configurable interval.
- Graceful Ctrl+C handling.
- Logging errors without immediate crash.
- Optional CSV output.

### 18.3 `examples/battery_check.py`

Demonstrate:

- Read battery percentage.
- Warn user if battery is low.

### 18.4 `examples/csv_measurement_logger.py`

Demonstrate:

- Command-line interval-based CSV logging.
- User-defined COM port.
- User-defined output file.
- User-defined interval.
- Optional finite duration.
- Append mode.
- Clean Ctrl+C shutdown.
- CSV output readable by Excel and pandas.

Required command-line usage example:

```bash
python examples/csv_measurement_logger.py --port COM16 --interval 1.0 --duration 3600 --output u1242c_log.csv
```

### 18.5 `examples/reconnect_logging.py`

Demonstrate:

- Long-running logging with retry and reconnect enabled.
- How communication errors are handled.
- How to continue measurement logging after a recoverable disconnect.

### 18.6 General Example Requirements

All examples shall:

- Be complete runnable scripts.
- Use `if __name__ == "__main__":`.
- Use `argparse` for user-configurable port/file/interval options where appropriate.
- Avoid hardcoded `COM16` except as a documented example default.
- Handle Ctrl+C gracefully.
- Avoid swallowing exceptions silently.
- Be included in packaging or documented as examples.
- Support `--help` without connecting to real hardware.
- Avoid import-time hardware access; serial connection shall occur only inside main execution paths.

### 18.7 `examples/hardware_smoke_test.py`

Provide an optional real-hardware smoke-test script. This script shall not be part of normal `pytest` and shall require the user to explicitly provide a port. It shall query:

```text
*IDN?
STAT?
CONF?
SYST:BATT?
FETC?
```

The script shall print a compact diagnostic report with identity, raw status, parsed configuration, battery percentage, and one parsed measurement. It shall be useful for verifying a new adapter/PC setup before a long logging run.

Required command-line usage example:

```bash
python examples/hardware_smoke_test.py --port COM16
```

The script shall support `--help` without connecting to real hardware.

### 18.8 CLI Entry Point

The installable package shall provide a console script named `u1242c-log` through `pyproject.toml`. The CLI shall be implemented in `src/keysight_u1242c/cli.py` and shall reuse the public driver API, not duplicate low-level serial logic.

Required CLI behavior:

```bash
u1242c-log --help
u1242c-log --port COM16 --once
u1242c-log --port COM16 --interval 1.0 --output u1242c_log.csv
u1242c-log --port COM16 --interval 1.0 --duration 3600 --output u1242c_log.csv --append
u1242c-log --port COM16 --hardware-check
```

The CLI shall:

- Support `--help` without hardware.
- Return non-zero exit code on unrecoverable communication errors.
- Print user-facing errors clearly.
- Use the package logger/debug option for verbose diagnostics.
- Be tested with argument parsing and help output without requiring hardware.

---

## 19. Documentation Requirements

The AI agent shall generate user-facing documentation for the package API and examples. Documentation must be accurate enough that a user can install the package, connect to the meter, read a measurement, log data to CSV, and handle errors without reading the source code.

### 19.1 API Documentation

Create `docs/api.md` with documentation for all public classes, dataclasses, methods, parameters, return values, and exceptions. At minimum, document:

- `KeysightU1242C` constructor parameters.
- `connect()` / `close()` / `is_connected()`.
- `identify()`.
- `get_status_raw()` and `get_status()`.
- `get_config()` and `get_configuration()`.
- `measure_raw()` and `measure()`.
- `get_battery_percent()`.
- `reset()`, `beep()`, `set_backlight()`.
- `query()` and `send()`.
- `log_measurements_csv(...)`.
- `Measurement`, `Configuration`, and `Status` dataclasses.
- All custom exceptions.
- Deprecated compatibility aliases and migration notes.

### 19.2 CSV Logging Documentation

Create `docs/logging.md` with:

- CSV logger purpose.
- Column description.
- Example command line usage.
- Example Python API usage.
- Example pandas loading code.
- Notes about Excel compatibility.
- Notes about logging intervals, timeout, retry, reconnect, and battery behavior.

### 19.3 Production Notes

Create `docs/production_notes.md` with:

- Recommended timeout settings.
- USB/serial adapter stability recommendations.
- Battery and long-test recommendations.
- Reconnect behavior.
- File logging and data-loss reduction.
- Known limitations of undocumented status decoding.

### 19.4 README Requirements

`README.md` shall include:

1. Project purpose.
2. Supported instrument.
3. Installation instructions.
4. Basic usage example.
5. Continuous logging example.
6. CSV measurement logging example with defined interval and timestamp.
7. Example showing how to load the CSV file in pandas.
8. Error handling example.
9. API overview with link/reference to `docs/api.md`.
10. Notes about USB/serial adapter stability.
11. Explanation of timeout/retry/reconnect parameters.
12. Warning that SCPI command support depends on instrument firmware/interface behavior.
13. Production-use checklist.

---

### 19.5 GitHub Repository Markdown Requirements

The AI agent shall generate Markdown files suitable for publishing the package as a clean GitHub repository. These files shall be written in clear technical English and shall be useful for both users and future maintainers.

Required repository files:

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
SUPPORT.md
.gitignore
LICENSE
docs/api.md
docs/logging.md
docs/production_notes.md
```

#### `README.md`

`README.md` shall be the main GitHub landing page and shall include:

1. Project title and short description.
2. Supported instrument: Keysight/Agilent U1242C.
3. Main features list.
4. Installation instructions using `pip install -e .`.
5. Quick-start example.
6. CSV logging example.
7. Example CSV format.
8. pandas loading example.
9. Error handling example.
10. Links to `docs/api.md`, `docs/logging.md`, and `docs/production_notes.md`.
11. Production-use checklist.
12. Test instructions using `pytest`.
13. Note that tests do not require real hardware.
14. Known limitations, including undocumented `STAT?` bit meanings.
15. License placeholder or instruction to add a license before public release.

#### `CHANGELOG.md`

`CHANGELOG.md` shall follow a simple human-readable format inspired by Keep a Changelog. It shall include at minimum:

```markdown
# Changelog

## Unreleased

### Added
- Production-grade package structure.
- Serial transport abstraction.
- Retry and reconnect handling.
- Typed measurement/configuration/status dataclasses.
- CSV measurement logging.
- Examples and documentation.

### Changed
- Replaced prototype `u1242c` class with `KeysightU1242C`.

### Deprecated
- Deprecated compatibility aliases for old method names, if implemented.
```

#### `CONTRIBUTING.md`

`CONTRIBUTING.md` shall include:

1. How to set up a development environment.
2. How to install in editable mode.
3. How to run tests.
4. How to run formatting.
5. How to add fake-serial tests without hardware.
6. Rules for adding new instrument commands.
7. Rule that undocumented status bits shall not be guessed.
8. Pull request checklist.

#### `SUPPORT.md`

`SUPPORT.md` shall include:

1. What information to provide when reporting communication problems.
2. Recommended debug log settings.
3. Required details: OS, Python version, pyserial version, COM port, adapter type, baudrate, timeout, command trace, and device firmware version from `*IDN?`.
4. Basic troubleshooting steps for no response, timeout, wrong COM port, low battery, and USB disconnects.

#### `.gitignore`

Generate a Python-focused `.gitignore` suitable for direct GitHub use. It shall ignore at minimum:

```text
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
venv/
build/
dist/
*.egg-info/
.coverage
htmlcov/
*.log
*.csv
```

CSV log files are generated user data and shall not be committed by default.

#### `LICENSE`

Generate a `LICENSE` file. If the final license is unknown, use a clear placeholder such as:

```text
License not selected yet. Choose and add an appropriate open-source or proprietary license before public release.
```

Do not falsely claim a license that the maintainer did not choose.

#### General Markdown Quality Requirements

All generated Markdown files shall:

- Use clear headings and fenced code blocks.
- Avoid references to non-existent files or APIs.
- Match the final generated package structure exactly.
- Avoid overpromising unsupported functionality.
- Clearly separate verified real-device behavior from assumptions or future work.
- Be suitable for direct commit to a GitHub repository.

---

## 20. Production-Use Checklist

Include this checklist in README:

```text
[ ] Use stable USB/serial adapter.
[ ] Use powered USB hub if required.
[ ] Set timeout >= 1 second for slow measurements.
[ ] Enable logging to file.
[ ] Enable auto_reconnect for long tests.
[ ] Check battery before long unattended test.
[ ] Use external power if supported by the instrument/interface.
[ ] Test disconnect/reconnect behavior before deployment.
[ ] Validate measurement format with the real U1242C.
[ ] Run unit tests before release.
```

---

## 21. Coding Style Requirements

- Python 3.10+.
- Use type hints.
- Use dataclasses where useful.
- Use `logging`, not `print()`.
- Use `pathlib` where file paths are required.
- Keep functions small and testable.
- Avoid broad `except:` blocks.
- Do not hide communication failures silently.
- Use clear names and docstrings.
- Format code with `black`.
- Keep import order clean.

---

## 21.1 Final Production Clarifications

These clarifications are mandatory and override any earlier ambiguous wording in this document.

1. **Exception naming:** Do not create a user-facing custom exception named `ConnectionError`. Use `InstrumentConnectionError` to avoid shadowing Python built-ins.
2. **Response normalization:** All received lines shall be decoded with the configured encoding, then stripped of serial terminators. Parser dataclasses shall preserve normalized raw text, not trailing line endings.
3. **Port validation:** COM-port existence validation shall be optional. Production systems may use virtual ports that are not reliably visible through enumeration.
4. **Side-effect safety:** Query retries are allowed by default. Side-effect command retries shall be conservative and disabled by default unless the implementation can prove the command was not sent.
5. **CSV schedule safety:** CSV logging shall never overlap measurements. Slow samples shall be logged with actual timestamps and warning messages when the schedule falls behind.
6. **Dependencies:** `pyserial` is a runtime dependency. `pytest` and `pandas` are test/development dependencies. Normal measurement and CSV logging shall not require pandas.
7. **Examples:** Examples must be import-safe and support `--help` without hardware. Hardware access must happen only after the user provides a real port/run command.
8. **Parser separation:** Parsing shall live in a testable `parsers.py` module or equally isolated pure functions. Parser tests shall not require serial transport.
9. **CLI:** The package shall provide a tested `u1242c-log` console entry point for one-shot measurement, CSV logging, and optional hardware check.
10. **Repository support files:** Generate `.gitignore` and `LICENSE` together with GitHub Markdown documentation.
11. **CSV metadata caching:** Long-running CSV logging shall cache slow-changing metadata and refresh it at configurable intervals to avoid unnecessary serial traffic.

---

## 22. Acceptance Criteria

The task is complete only when:

1. Package installs successfully with `pip install -e .`.
2. `pytest` passes without real hardware.
3. Public class `KeysightU1242C` exists.
4. Context manager usage works.
5. Existing basic commands are supported.
6. Old compatibility methods are available or documented as intentionally removed.
7. Serial communication has timeout, retry, and reconnect handling.
8. Driver never uses `print()` internally.
9. Driver does not call long blocking sleeps for battery warnings.
10. Empty responses raise a clear custom exception.
11. Serial exceptions are converted to custom driver exceptions.
12. `close()` is safe to call repeatedly.
13. README contains usage examples and production checklist.
14. Example scripts run without syntax errors.
15. Continuous logging example handles Ctrl+C gracefully.
16. `STAT?` command is implemented and tested.
17. `CONF?` response `"TEMP:K CEL"` is parsed into function, sensor, and unit.
18. `FETC?` response `+2.37400000E+01` is parsed into `23.74`.
19. Measurement objects preserve raw response and include configuration-derived unit/function when available.
20. Real-device trace regression tests pass without real hardware.
21. `examples/` contains complete runnable scripts for basic use, battery check, continuous logging, CSV logging, and reconnect logging.
22. `docs/api.md` documents all public APIs, dataclasses, parameters, return values, and exceptions.
23. `docs/logging.md` documents CSV logging, columns, Excel compatibility, and pandas usage.
24. CSV logger can write timestamped measurements at a user-defined interval.
25. Generated CSV can be opened in Excel and read by `pandas.read_csv()` without custom parsing.
26. CSV logger includes ISO timestamp, Unix timestamp, elapsed time, measurement value, unit, function, raw measurement, status, battery, and error column.
27. CSV logger handles Ctrl+C, finite duration, append mode, and sample errors cleanly.
28. Custom exception names do not shadow Python built-ins; use `InstrumentConnectionError` instead of `ConnectionError`.
29. Constructor supports `strict_parsing`, configurable battery thresholds, optional COM-port validation, and configurable response encoding.
30. Side-effect commands are not blindly retried by default.
31. CSV logger handles interval overrun without overlapping measurement calls.
32. Runtime dependencies do not include pandas unless explicitly needed outside tests.
33. Example tests do not require real hardware.
34. Repository Markdown files `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `SUPPORT.md` are generated and match the final package structure.
35. GitHub README contains install, quick start, CSV logging, pandas loading, test, production checklist, and documentation links.
36. GitHub Markdown files are accurate, do not reference missing APIs/files, and are suitable for direct commit to a repository.
37. Repository contains a valid `pyproject.toml` and uses a `src/` layout.
38. Package installs successfully with `python -m pip install -e .`.
39. Package imports successfully from any working directory with `from keysight_u1242c import KeysightU1242C`.
40. Package builds successfully with `python -m build` into wheel and source distribution.
41. Example scripts import the package normally and do not rely on modifying `PYTHONPATH`.
42. Runtime dependencies are minimal and include `pyserial`; `pytest`, `black`, `ruff`, `pandas`, and `build` are development/test extras only.
43. Serial line/terminator requirements clearly specify `\r\n` for commands and stripping `\r`/`\n` from responses.
44. `parsers.py` or an equivalent pure parser layer exists and is directly unit-tested.
45. CSV logger supports metadata caching/refresh controls for configuration, status, and battery queries.
46. CSV logger does not query `CONF?`, `STAT?`, and `SYST:BATT?` unnecessarily on every sample unless configured to do so.
47. Package provides console script `u1242c-log` through `pyproject.toml`.
48. CLI supports `--help`, one-shot measurement, CSV logging, append mode, finite duration, and optional hardware check.
49. Repository contains `.gitignore` and `LICENSE` files suitable for GitHub use.
50. Optional hardware smoke test exists and is clearly separated from normal no-hardware unit tests.

---

## 23. Suggested Implementation Order

1. Create package structure with modern `src/` layout.
2. Create valid `pyproject.toml` for installable package `keysight-u1242c`.
3. Move command strings into `commands.py`.
4. Create custom exceptions.
5. Implement pure parser helpers in `parsers.py`.
6. Implement `SerialTransport`.
7. Implement `KeysightU1242C` using transport.
8. Export public API from `src/keysight_u1242c/__init__.py`.
9. Add structured logging.
10. Add CSV measurement logging API/helper with metadata caching.
11. Add context manager support.
12. Add CLI entry point in `cli.py`.
13. Add deprecated compatibility aliases if backward compatibility is kept.
14. Add unit tests with fake serial.
15. Add parser unit tests.
16. Add package import/install tests.
17. Add CSV logger tests.
18. Add CLI tests.
19. Add examples, including optional hardware smoke test.
20. Add README and API/logging/production documentation.
21. Add GitHub repository Markdown files: `CHANGELOG.md`, `CONTRIBUTING.md`, and `SUPPORT.md`.
22. Add repository support files: `.gitignore` and `LICENSE`.
23. Run formatting and tests.
24. Verify editable install with `python -m pip install -e .`.
25. Verify build with `python -m build`.
26. Verify CLI help with `u1242c-log --help`.
27. Review final API and repository documentation for production usability.

---

## 24. Non-Goals

Do not implement unrelated GUI functionality.

Do not add pyvisa support in this refactor unless explicitly requested later.

Do not assume unsupported commands beyond the currently known command set unless verified against the official instrument programming documentation.

Do not change the physical serial protocol terminator unless hardware testing proves it is required.

---

## 25. Real-Device Trace Regression Fixture

Create a test fixture file, for example:

```text
tests/fixtures/u1242c_real_trace_responses.txt
```

It shall include representative command/response pairs from real communication:

```text
*IDN?
Keysight Technologies,U1242C,MY57430015,V1.27
STAT?
"000000000900L00700000"
CONF?
"TEMP:K CEL"
SYST:BATT?
93%
FETC?
+2.37400000E+01
```

The tests shall verify that these samples are accepted by the parser and by the fake serial transport. The implementation shall not hard-code one specific serial number, battery value, or temperature value. These are examples for parser validation only.

---

## 26. Optional Future Enhancements

These are useful but not required for the first production refactor:

1. Add PyVISA backend support.
2. Add async API.
3. Add rotating log-file support.
4. Add instrument health monitor.
5. Add Prometheus/exporter metrics.
6. Add GUI status panel.
7. Add automatic COM-port detection by IDN scan.
8. Add configurable measurement validation rules.
9. Add support for more U124x-series models.
10. Add hardware-in-the-loop tests.

---

## 27. Expected Final Deliverable

The final deliverable shall be a clean, installable Python package named:

```text
keysight-u1242c
```

with import usage:

```python
from keysight_u1242c import KeysightU1242C

with KeysightU1242C("COM16") as dmm:
    print(dmm.identify())
    print(dmm.measure())
```

The final code shall be suitable for integration into a larger automated test platform and robust enough for long-duration measurement logging. It shall include complete examples, API documentation, and an easy CSV logging workflow with timestamped interval measurements readable by Excel and pandas.

The final repository shall also be immediately usable as a Python module/package:

```bash
python -m pip install -e .
python -c "from keysight_u1242c import KeysightU1242C"
python -m pytest
python -m build
u1242c-log --help
```

The repository shall include GitHub-ready documentation plus `.gitignore` and `LICENSE` files.

No manual copying of files or manual `PYTHONPATH` editing shall be required.
