"""Continuously print measurements until Ctrl+C."""

from __future__ import annotations

import argparse
import logging
import time

from keysight_u1242c import KeysightU1242C, KeysightU1242CError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--no-validate-port", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    with KeysightU1242C(port=args.port, validate_port_exists=not args.no_validate_port) as dmm:
        print("Press Ctrl+C to stop.")
        while True:
            try:
                measurement = dmm.measure()
                print(f"{measurement.value} {measurement.unit or ''}")
            except KeysightU1242CError as exc:
                logging.exception("Measurement failed: %s", exc)
            time.sleep(args.interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Stopped")
