"""Read one measurement from a Keysight U1242C."""

from __future__ import annotations

import argparse
import logging

from keysight_u1242c import KeysightU1242C


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True, help="Serial port, for example COM16")
    parser.add_argument("--no-validate-port", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    with KeysightU1242C(port=args.port, validate_port_exists=not args.no_validate_port) as dmm:
        print("IDN:", dmm.identify_raw())
        print("STAT:", dmm.get_status_raw())
        print("CONF:", dmm.get_configuration())
        print("BATT:", dmm.get_battery_percent())
        print("MEAS:", dmm.measure())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
