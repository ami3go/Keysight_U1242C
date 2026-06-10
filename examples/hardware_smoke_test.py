"""Optional hardware smoke test.

This script only connects when you explicitly pass a real --port argument.
It is not part of the normal pytest suite.
"""

from __future__ import annotations

import argparse

from keysight_u1242c.cli import run_hardware_check
from keysight_u1242c import KeysightU1242C


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--no-validate-port", action="store_true")
    args = parser.parse_args()

    with KeysightU1242C(port=args.port, validate_port_exists=not args.no_validate_port) as dmm:
        run_hardware_check(dmm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
