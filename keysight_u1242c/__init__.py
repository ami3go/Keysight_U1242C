"""Production-oriented serial driver for the Keysight U1242C DMM."""

from .driver import KeysightU1242C, u1242c
from .exceptions import (
    CommunicationError,
    InstrumentConnectionError,
    InvalidResponseError,
    KeysightU1242CError,
    ParseError,
    ResponseTimeoutError,
)
from .types import Configuration, Identity, Measurement, Status

__version__ = "0.1.0"

__all__ = [
    "KeysightU1242C",
    "u1242c",
    "Identity",
    "Measurement",
    "Configuration",
    "Status",
    "KeysightU1242CError",
    "InstrumentConnectionError",
    "CommunicationError",
    "ResponseTimeoutError",
    "InvalidResponseError",
    "ParseError",
]
