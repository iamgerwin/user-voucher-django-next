"""
Custom exception handler for DRF.
"""

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Args:
        exc: The exception instance
        context: The context in which the exception occurred

    Returns:
        Response object with formatted error message
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Standardize error response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': get_error_message(exc, response),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        response.data = custom_response_data

    return response


def get_error_message(exc, response):
    """
    Extract a user-friendly error message from the exception.

    Args:
        exc: The exception instance
        response: The response object

    Returns:
        String error message
    """
    if isinstance(exc, ValidationError):
        return 'Validation error occurred'

    if response.status_code == status.HTTP_404_NOT_FOUND:
        return 'Resource not found'

    if response.status_code == status.HTTP_403_FORBIDDEN:
        return 'Permission denied'

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return 'Authentication required'

    if response.status_code >= 500:
        return 'Internal server error'

    return 'An error occurred'
