# API Documentation

## `KeysightU1242C`

```python
KeysightU1242C(
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
)
```

## Main methods

- `connect(port=None) -> bool`
- `close() -> None`
- `is_connected() -> bool`
- `query(command) -> str`
- `send(command, side_effect=False) -> None`
- `identify_raw() -> str`
- `identify() -> Identity`
- `get_status_raw() -> str`
- `get_status() -> Status`
- `get_configuration_raw() -> str`
- `get_configuration() -> Configuration`
- `get_battery_raw() -> str`
- `get_battery_percent() -> float | None`
- `measure_raw() -> str`
- `measure(refresh_config=False) -> Measurement`
- `reset() -> None`
- `beep() -> None`
- `set_backlight(enabled) -> None`
- `log_measurements_csv(...) -> int`

## Typed return objects

`Measurement` contains `raw`, `value`, `unit`, `function`, and `config_raw`.

`Configuration` contains `raw`, `function`, `sensor`, and `unit`.

`Status` contains `raw` and `normalized`. The status bit meaning is intentionally not decoded without official documentation.
