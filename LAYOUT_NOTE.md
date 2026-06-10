# Layout note

This package intentionally uses a flat package layout requested by the user:

```text
keysight-u1242c-repo/
  keysight_u1242c/
  tests/
  examples/
  docs/
  pyproject.toml
```

The original v1.6 AI task requested a `src/` layout, but this generated package was adjusted so the driver package lives directly in the repository root while remaining installable via `pyproject.toml`.

Install with:

```bash
python -m pip install -e .
```
