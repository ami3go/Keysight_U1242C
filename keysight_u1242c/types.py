"""Typed response objects returned by the Keysight U1242C driver."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    """Parsed `*IDN?` response."""

    raw: str
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    firmware_version: str | None = None


@dataclass(frozen=True)
class Status:
    """Status response from `STAT?`.

    The bit/string meaning is intentionally not decoded without official mapping.
    """

    raw: str
    normalized: str


@dataclass(frozen=True)
class Configuration:
    """Parsed `CONF?` response."""

    raw: str
    function: str | None = None
    sensor: str | None = None
    unit: str | None = None


@dataclass(frozen=True)
class Measurement:
    """Parsed `FETC?` response."""

    raw: str
    value: float | None = None
    unit: str | None = None
    function: str | None = None
    config_raw: str | None = None


@dataclass(frozen=True)
class CsvLogRow:
    """One CSV logger row."""

    timestamp_iso: str
    unix_time_s: float
    elapsed_s: float
    measurement_value: float | None
    unit: str | None
    function: str | None
    config_raw: str | None
    status_raw: str | None
    battery_percent: float | None
    measurement_raw: str | None
    error: str | None = None
