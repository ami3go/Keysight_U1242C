"""Check Keysight U1242C battery percentage."""

from __future__ import annotations

import argparse
import logging

from keysight_u1242c import KeysightU1242C


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--low", type=float, default=30.0)
    parser.add_argument("--critical", type=float, default=15.0)
    parser.add_argument("--no-validate-port", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    with KeysightU1242C(
        port=args.port,
        battery_low_warning_percent=args.low,
        battery_critical_warning_percent=args.critical,
        validate_port_exists=not args.no_validate_port,
    ) as dmm:
        battery = dmm.get_battery_percent()
        print(f"Battery: {battery}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
