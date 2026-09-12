class ReportGeneratorError(Exception):
    """Base application error."""


class InputDataError(ReportGeneratorError):
    """Raised for malformed or invalid source data."""


class ApiError(ReportGeneratorError):
    """Raised when a remote API cannot be consumed."""


class ReportOutputError(ReportGeneratorError):
    """Raised when an output report cannot be written."""
