import csv
import threading

import pandas as pd

from keysight_u1242c import KeysightU1242C
from keysight_u1242c.driver import CSV_COLUMNS
from .fakes import REAL_TRACE_RESPONSES, response_factory


def make_dmm():
    dmm = KeysightU1242C(
        port="COM16",
        serial_factory=response_factory(REAL_TRACE_RESPONSES),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    return dmm


def test_csv_logger_creates_header_and_rows(tmp_path):
    dmm = make_dmm()
    output = tmp_path / "log.csv"
    rows = dmm.log_measurements_csv(output, interval_s=0.001, max_samples=2)
    assert rows == 2
    with output.open(newline="") as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == CSV_COLUMNS
        data = list(reader)
    assert len(data) == 2
    assert data[0]["measurement_value"] == "23.74"
    assert data[0]["unit"] == "CEL"


def test_csv_logger_pandas_readable(tmp_path):
    dmm = make_dmm()
    output = tmp_path / "log.csv"
    dmm.log_measurements_csv(output, interval_s=0.001, max_samples=1)
    df = pd.read_csv(output)
    assert list(df.columns) == CSV_COLUMNS
    assert df.loc[0, "measurement_value"] == 23.74


def test_csv_logger_append_without_duplicate_header(tmp_path):
    dmm = make_dmm()
    output = tmp_path / "log.csv"
    dmm.log_measurements_csv(output, interval_s=0.001, max_samples=1)
    dmm.log_measurements_csv(output, interval_s=0.001, max_samples=1, append=True)
    lines = output.read_text().splitlines()
    assert lines[0].startswith("timestamp_iso")
    assert sum(1 for line in lines if line.startswith("timestamp_iso")) == 1
    assert len(lines) == 3


def test_csv_logger_error_row_on_failed_sample(tmp_path):
    responses = REAL_TRACE_RESPONSES | {"FETC?": ""}
    dmm = KeysightU1242C(
        port="COM16",
        retries=0,
        serial_factory=response_factory(responses),
        list_ports_provider=lambda: ["COM16"],
    )
    dmm.connect()
    output = tmp_path / "log.csv"
    dmm.log_measurements_csv(output, interval_s=0.001, max_samples=1)
    rows = list(csv.DictReader(output.open(newline="")))
    assert rows[0]["error"]


def test_csv_logger_stop_event(tmp_path):
    dmm = make_dmm()
    stop = threading.Event()
    stop.set()
    output = tmp_path / "log.csv"
    rows = dmm.log_measurements_csv(output, interval_s=1, stop_event=stop)
    assert rows == 0
