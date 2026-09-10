# Keysight_U1242C

SCPI driver for the Keysight U1242C handheld digital multimeter, talking over
its USB-serial interface.

Built on [scpi-driver-core](https://github.com/ami3go/scpi-driver-core) for
transport, framing, and session handling; this repo only adds the
U1242C-specific commands.

Reference: https://sigrok.org/wiki/Agilent_U12xxx_series

## Requirements

- Python 3.10+
- The instrument connected over USB, enumerating as a serial port
  (`/dev/ttyUSB*` on Linux, `COMx` on Windows).
- On Linux, your user typically needs to be in the `dialout` group to open
  the port: `sudo usermod -aG dialout $USER` (re-login, or `newgrp dialout`,
  for it to take effect).

## Install

As a dependency, straight from GitHub:

```bash
pip install "git+https://github.com/ami3go/Keysight_U1242C.git"
```

From a local clone:

```bash
git clone https://github.com/ami3go/Keysight_U1242C.git
cd Keysight_U1242C
pip install .        # or `pip install -e .` for an editable/development install
```

Either way this pulls in `scpi-driver-core[serial]` (which includes
`pyserial`) straight from GitHub, since the core library is not yet published
on PyPI.

## Usage

```python
from keysight_u1242c import U1242C

with U1242C("/dev/ttyUSB0") as dmm:
    print(dmm.get_data())
```

`U1242C.__init__` never touches the port; `init()` (or the `with` block) opens
it, confirms the instrument answers `*IDN?`, and reports its configuration and
battery level. Connection failures raise `scpi_driver_core` exceptions
(`ScpiDriverError` and subclasses) instead of returning `False`.

### API

| Method | SCPI | Description |
| --- | --- | --- |
| `init()` | `*IDN?` | Open the connection and report identity/config/battery. Called automatically by `with U1242C(...)`. |
| `close()` | – | Close the connection. Called automatically at the end of a `with` block. |
| `get_data()` | `FETC?` | Current primary measurement, as `float`. |
| `get_conf()` | `CONF?` | Active measurement configuration, as `str`. |
| `get_battery_percent()` | `SYST:BATT?` | Remaining battery charge, as `float` percentage. |
| `reset()` | `*RST` | Return the instrument to its power-on default state. |
| `beep()` | `SYST:BEEP` | Sound the instrument's beeper once. |
| `back_light(on: bool)` | `SYST:BLIT` | Turn the display backlight on or off. |

See `Example/main.py` for a full example that logs measurements to a CSV file.
