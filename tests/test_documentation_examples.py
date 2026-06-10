import py_compile
from pathlib import Path


EXAMPLES = [
    "basic_measurement.py",
    "continuous_logging.py",
    "battery_check.py",
    "csv_measurement_logger.py",
    "reconnect_logging.py",
    "hardware_smoke_test.py",
]


def test_examples_compile():
    root = Path(__file__).resolve().parents[1]
    for example in EXAMPLES:
        py_compile.compile(str(root / "examples" / example), doraise=True)


def test_docs_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "README.md").exists()
    assert (root / "docs" / "api.md").exists()
    assert (root / "docs" / "logging.md").exists()
    assert (root / "docs" / "production_notes.md").exists()
