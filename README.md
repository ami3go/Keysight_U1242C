# keysight-u1242c

Production-oriented Python serial driver for the Keysight/Agilent U1242C handheld digital multimeter.

The package replaces a simple script-style serial class with a testable installable module that supports:

- `*IDN?`, `STAT?`, `CONF?`, `SYST:BATT?`, and `FETC?`
- typed parsers for identity, status, configuration, battery, and measurement
- retry and optional reconnect behavior
- context manager cleanup
- CSV logging with timestamp, elapsed time, battery, status, config, raw values, and error column
- command-line logging through `u1242c-log`
- unit tests with fake serial transport, no hardware required


## Repository layout

This repository uses a flat installable package layout, as requested:

```text
keysight_u1242c/
tests/
examples/
docs/
pyproject.toml
```

The package is installable directly from the repository root with `python -m pip install -e .`.

## Installation

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e .[dev]
python -m pytest
```

## Basic usage

```python
from keysight_u1242c import KeysightU1242C

with KeysightU1242C(port="COM16") as dmm:
    print(dmm.identify_raw())
    print(dmm.get_status_raw())
    print(dmm.get_configuration())
    print(dmm.get_battery_percent())
    print(dmm.measure())
```

## CSV logging

```python
from keysight_u1242c import KeysightU1242C

with KeysightU1242C(port="COM16") as dmm:
    dmm.log_measurements_csv(
        "u1242c_log.csv",
        interval_s=1.0,
        duration_s=3600,
    )
```

Command line:

```bash
u1242c-log --port COM16 --interval 1.0 --duration 3600 --output u1242c_log.csv
u1242c-log --port COM16 --once
u1242c-log --port COM16 --hardware-check
```

## CSV columns

```text
timestamp_iso,unix_time_s,elapsed_s,measurement_value,unit,function,config_raw,status_raw,battery_percent,measurement_raw,error
```

The CSV is designed to open directly in Excel or LibreOffice Calc and load with:

```python
import pandas as pd
df = pd.read_csv("u1242c_log.csv")
```

`pandas` is not required at runtime; it is only a development/test dependency.

## Real trace examples

The driver includes parser support for observed real-device responses:

```text
*IDN?       -> Keysight Technologies,U1242C,MY57430015,V1.27
STAT?       -> "000000000900L00700000"
CONF?       -> "TEMP:K CEL"
SYST:BATT?  -> 93%
FETC?       -> +2.37400000E+01
```

## Production notes

For 24/7 use, keep logging enabled, use a realistic timeout such as 2 seconds or higher, and prefer `auto_reconnect=True`. Side-effect commands such as reset, beep, and backlight are not blindly retried by default.
