"""Demonstrate reconnect-enabled CSV logging."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from keysight_u1242c import KeysightU1242C


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--interval", type=float, default=1.0)
    parser.add_argument("--duration", type=float, default=3600.0)
    parser.add_argument("--output", type=Path, default=Path("u1242c_reconnect_log.csv"))
    parser.add_argument("--no-validate-port", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    with KeysightU1242C(
        port=args.port,
        auto_reconnect=True,
        retries=3,
        retry_delay=0.5,
        validate_port_exists=not args.no_validate_port,
    ) as dmm:
        dmm.log_measurements_csv(args.output, interval_s=args.interval, duration_s=args.duration)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
