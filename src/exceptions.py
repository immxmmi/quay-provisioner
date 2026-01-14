"""Custom exceptions for the Pipeline Execution Platform."""


class PipelineError(Exception):
    """Base exception for all pipeline-related errors."""
    pass


class ConfigurationError(PipelineError):
    """Raised when configuration is invalid or missing."""
    pass


class ValidationError(PipelineError):
    """Raised when input validation fails."""
    pass

