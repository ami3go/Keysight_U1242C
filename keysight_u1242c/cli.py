"""Command-line interface for the Keysight U1242C package."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .driver import KeysightU1242C
from .exceptions import KeysightU1242CError


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="u1242c-log",
        description="Read or log measurements from a Keysight U1242C serial DMM.",
    )
    parser.add_argument("--port", required=True, help="Serial port, for example COM16 or /dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=9600, help="Serial baudrate, default 9600")
    parser.add_argument("--timeout", type=float, default=2.0, help="Serial read timeout in seconds")
    parser.add_argument("--interval", type=float, default=1.0, help="Logging interval in seconds")
    parser.add_argument("--duration", type=float, default=None, help="Optional logging duration in seconds")
    parser.add_argument("--output", type=Path, default=Path("u1242c_log.csv"), help="CSV output path")
    parser.add_argument("--append", action="store_true", help="Append to existing CSV file")
    parser.add_argument("--once", action="store_true", help="Read and print one measurement")
    parser.add_argument("--hardware-check", action="store_true", help="Run IDN/STAT/CONF/BATT/FETC check")
    parser.add_argument(
        "--no-validate-port",
        action="store_true",
        help="Skip COM-port enumeration and open the given port directly",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def run_hardware_check(dmm: KeysightU1242C) -> None:
    print("Hardware check")
    print("==============")
    print(f"IDN:    {dmm.identify_raw()}")
    print(f"STAT:   {dmm.get_status_raw()}")
    print(f"CONF:   {dmm.get_configuration_raw()}")
    print(f"BATT:   {dmm.get_battery_raw()}")
    print(f"FETC:   {dmm.measure_raw()}")


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        with KeysightU1242C(
            port=args.port,
            baudrate=args.baudrate,
            timeout=args.timeout,
            validate_port_exists=not args.no_validate_port,
        ) as dmm:
            if args.hardware_check:
                run_hardware_check(dmm)
                return 0
            if args.once:
                measurement = dmm.measure(refresh_config=True)
                print(
                    f"{measurement.value} {measurement.unit or ''} "
                    f"({measurement.function or 'unknown function'})"
                )
                return 0
            dmm.log_measurements_csv(
                output_path=args.output,
                interval_s=args.interval,
                duration_s=args.duration,
                append=args.append,
            )
            return 0
    except KeyboardInterrupt:
        print("Interrupted by user", file=sys.stderr)
        return 130
    except KeysightU1242CError as exc:
        print(f"U1242C error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
