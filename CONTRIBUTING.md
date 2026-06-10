# Contributing

## Development setup

```bash
python -m pip install -e .[dev]
python -m pytest
```

## Style

Use clear type hints, keep serial communication isolated in `transport.py`, and keep parser functions pure and covered by tests.

## Hardware tests

Normal tests must not require real hardware. Use `examples/hardware_smoke_test.py` or `u1242c-log --hardware-check` for manual validation with a real meter.
