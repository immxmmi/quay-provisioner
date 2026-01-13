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


class QuayApiError(PipelineError):
    """Base exception for Quay API errors."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class ResourceNotFoundError(QuayApiError):
    """Raised when a requested resource does not exist."""
    pass


class OrganizationNotFoundError(ResourceNotFoundError):
    """Raised when an organization does not exist."""
    pass


class RobotNotFoundError(ResourceNotFoundError):
    """Raised when a robot account does not exist."""
    pass


class TeamNotFoundError(ResourceNotFoundError):
    """Raised when a team does not exist."""
    pass


class ResourceAlreadyExistsError(QuayApiError):
    """Raised when trying to create a resource that already exists."""
    pass


class OrganizationAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when an organization already exists."""
    pass


class RobotAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when a robot account already exists."""
    pass


class TeamAlreadyExistsError(ResourceAlreadyExistsError):
    """Raised when a team already exists."""
    pass
