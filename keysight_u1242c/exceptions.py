"""Exception hierarchy for the Keysight U1242C driver."""


class KeysightU1242CError(Exception):
    """Base exception for all driver errors."""


class InstrumentConnectionError(KeysightU1242CError):
    """Raised when the instrument cannot be connected or connection is lost."""


class CommunicationError(KeysightU1242CError):
    """Raised when serial communication fails."""


class ResponseTimeoutError(CommunicationError):
    """Raised when the instrument does not return a response before timeout."""


class InvalidResponseError(CommunicationError):
    """Raised when a response is empty, malformed, or unexpected."""


class ParseError(InvalidResponseError):
    """Raised when a response cannot be parsed in strict parsing mode."""
