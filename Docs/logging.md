# CSV Logging

The driver can write long-duration measurement logs with timestamped rows.

```python
with KeysightU1242C(port="COM16") as dmm:
    rows = dmm.log_measurements_csv(
        "u1242c_log.csv",
        interval_s=1.0,
        duration_s=3600,
        append=False,
    )
```

## Columns

```text
timestamp_iso,unix_time_s,elapsed_s,measurement_value,unit,function,config_raw,status_raw,battery_percent,measurement_raw,error
```

Errors are written into the `error` column by default so failed samples are visible instead of silently dropped.

## Metadata refresh

`FETC?` is queried for every sample. `CONF?`, `STAT?`, and `SYST:BATT?` can be cached and refreshed at configurable intervals:

```python
dmm.log_measurements_csv(
    "log.csv",
    interval_s=1.0,
    config_refresh_s=60.0,
    status_refresh_s=10.0,
    battery_refresh_s=300.0,
)
```

## pandas

```python
import pandas as pd
df = pd.read_csv("u1242c_log.csv")
```
