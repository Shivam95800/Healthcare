"""
Standardized error handling for CareOS Healthcare Backend.
Formats all exceptions into:
{
    "success": false,
    "message": "Human readable error description",
    "errors": { ... }
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.http import Http404

def custom_exception_handler(exc, context):
    """
    Custom exception handler to return consistent error responses across all APIs.
    """
    # Call REST framework's default exception handler first to get standard response
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred."
        errors = {}

        if isinstance(response.data, dict):
            # If detail is present
            if 'detail' in response.data:
                message = str(response.data['detail'])
                errors = {'detail': [message]}
            else:
                errors = response.data
                # Pick the first error message for top-level readability
                try:
                    first_key = next(iter(response.data))
                    first_val = response.data[first_key]
                    if isinstance(first_val, list) and len(first_val) > 0:
                        message = f"{first_key}: {first_val[0]}"
                    elif isinstance(first_val, str):
                        message = f"{first_key}: {first_val}"
                    else:
                        message = f"Validation failed on {first_key}."
                except (StopIteration, Exception):
                    message = "Validation error."
        elif isinstance(response.data, list):
            errors = {'non_field_errors': response.data}
            message = str(response.data[0]) if response.data else "Validation failed."
        else:
            message = str(response.data)
            errors = {'detail': [message]}

        # Map 401/403/404 friendly messages if needed
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            if not message or message == "An error occurred.":
                message = "Authentication credentials were not provided or are invalid."
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            if not message or message == "An error occurred.":
                message = "You do not have permission to perform this action."
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            if not message or message == "An error occurred.":
                message = "The requested resource was not found."

        response.data = {
            'success': False,
            'message': message,
            'errors': errors
        }

    return response
