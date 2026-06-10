import os
import subprocess
import sys
from pathlib import Path


def test_hardware_smoke_help_does_not_connect():
    root = Path(__file__).resolve().parents[1]
    script = root / "examples" / "hardware_smoke_test.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root / "src") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True, env=env)
    assert result.returncode == 0
    assert "--port" in result.stdout
