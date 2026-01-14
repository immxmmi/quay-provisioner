"""Base class for all pipeline actions."""

from abc import ABC, abstractmethod
from typing import Any

from exceptions import ValidationError
from model.action_response import ActionResponse


class BaseAction(ABC):
    """Abstract base class for all pipeline actions.

    Provides common functionality:
    - Gateway dependency injection
    - Required field validation
    - Standardized execute interface
    """

    def __init__(self, gateway=None):
        """
        Args:
            gateway: External gateway client to be used by the action.
        """
        self.gateway = gateway

    @abstractmethod
    def execute(self, data: dict) -> ActionResponse:
        """Execute the action with the provided data.

        Args:
            data: Dictionary containing action parameters

        Returns:
            ActionResponse with success status and optional data/message
        """
        pass

    def validate_required(self, data: dict, *fields: str) -> None:
        """Validate that all required fields are present and non-empty.

        Args:
            data: Dictionary to validate
            *fields: Field names that must be present

        Raises:
            ValidationError: If any required field is missing or empty
        """
        for field in fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                raise ValidationError(f"Missing required field: '{field}'")

    def get_required(self, data: dict, field: str, field_type: type = str) -> Any:
        """Get a required field value with type validation.

        Args:
            data: Dictionary to get value from
            field: Field name to retrieve
            field_type: Expected type of the field

        Returns:
            The field value

        Raises:
            ValidationError: If field is missing or wrong type
        """
        value = data.get(field)
        if value is None:
            raise ValidationError(f"Missing required field: '{field}'")
        if not isinstance(value, field_type):
            raise ValidationError(f"Field '{field}' must be of type {field_type.__name__}")
        return value
