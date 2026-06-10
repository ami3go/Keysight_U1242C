"""Pure parsers for Keysight U1242C responses.

The functions in this module do not touch serial hardware. They are intentionally
small and independently testable because instrument protocols often produce
surprising edge cases during long unattended runs.
"""

from __future__ import annotations

import re

from .exceptions import ParseError
from .types import Configuration, Identity, Measurement, Status

_NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$")


def normalize_response(raw: str | bytes | None, encoding: str = "ascii") -> str:
    """Decode and strip one line response.

    Serial line terminators are not preserved in typed `raw` fields. Surrounding
    whitespace is stripped, but quotes inside the response are left for the
    individual parsers to interpret.
    """

    if raw is None:
        return ""
    if isinstance(raw, bytes):
        raw = raw.decode(encoding, errors="replace")
    return str(raw).strip()


def strip_quotes(value: str) -> str:
    """Strip one surrounding single or double quote pair if present."""

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _raise_or_none(message: str, strict: bool) -> None:
    if strict:
        raise ParseError(message)
    return None


def parse_identity(raw: str, strict: bool = False) -> Identity:
    """Parse an `*IDN?` response.

    Example: ``Keysight Technologies,U1242C,MY57430015,V1.27``.
    """

    normalized = normalize_response(raw)
    parts = [p.strip() for p in normalized.split(",")]
    if len(parts) >= 4:
        return Identity(
            raw=normalized,
            manufacturer=parts[0] or None,
            model=parts[1] or None,
            serial_number=parts[2] or None,
            firmware_version=",".join(parts[3:]).strip() or None,
        )
    _raise_or_none(f"Cannot parse identity response: {normalized!r}", strict)
    return Identity(raw=normalized)


def parse_status(raw: str, strict: bool = False) -> Status:
    """Parse a `STAT?` response.

    The observed hardware returns strings such as ``"000000000900L00700000"``.
    The content is preserved because the bit/string mapping is not specified.
    """

    normalized = strip_quotes(normalize_response(raw))
    if not normalized:
        _raise_or_none("Empty status response", strict)
    return Status(raw=normalize_response(raw), normalized=normalized)


def parse_configuration(raw: str, strict: bool = False) -> Configuration:
    """Parse a `CONF?` response.

    Example: ``"TEMP:K CEL"`` -> function ``TEMP:K``, sensor ``K``, unit ``CEL``.
    Unknown formats return a Configuration with only ``raw`` unless strict mode is enabled.
    """

    normalized = normalize_response(raw)
    content = strip_quotes(normalized)
    if not content:
        _raise_or_none("Empty configuration response", strict)
        return Configuration(raw=normalized)

    tokens = content.split()
    primary = tokens[0] if tokens else ""
    unit = tokens[1] if len(tokens) > 1 else None

    function: str | None = None
    sensor: str | None = None
    if primary:
        if ":" in primary:
            base, sensor_text = primary.split(":", 1)
            function = f"{base}:{sensor_text}" if sensor_text else base
            sensor = sensor_text or None
        else:
            function = primary

    if function is None and unit is None:
        _raise_or_none(f"Cannot parse configuration response: {normalized!r}", strict)

    return Configuration(raw=normalized, function=function, sensor=sensor, unit=unit)


def parse_battery_percent(raw: str, strict: bool = False) -> float | None:
    """Parse a `SYST:BATT?` response into a percentage float.

    Example: ``93%`` -> ``93.0``.
    """

    normalized = strip_quotes(normalize_response(raw))
    if not normalized:
        _raise_or_none("Empty battery response", strict)
        return None

    value_text = normalized.replace("%", "").strip()
    try:
        value = float(value_text)
    except ValueError:
        _raise_or_none(f"Cannot parse battery response: {normalized!r}", strict)
        return None

    if not 0.0 <= value <= 100.0:
        _raise_or_none(f"Battery percent out of range: {value!r}", strict)
        return None
    return value


def parse_measurement(
    raw: str,
    config: Configuration | None = None,
    strict: bool = False,
) -> Measurement:
    """Parse a `FETC?` response.

    Numeric-only responses such as ``+2.37400000E+01`` derive unit/function from
    the supplied configuration, if present.
    """

    normalized = normalize_response(raw)
    content = strip_quotes(normalized)
    if not content:
        _raise_or_none("Empty measurement response", strict)
        return Measurement(raw=normalized)

    first_token = content.split()[0]
    value: float | None = None
    if _NUMERIC_RE.match(first_token):
        value = float(first_token)
    else:
        _raise_or_none(f"Cannot parse measurement response: {normalized!r}", strict)

    return Measurement(
        raw=normalized,
        value=value,
        unit=config.unit if config else None,
        function=config.function if config else None,
        config_raw=config.raw if config else None,
    )
