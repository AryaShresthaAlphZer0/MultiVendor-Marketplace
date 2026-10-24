from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class InsufficientStock(APIException):
    """Raised when an order or cart quantity exceeds available stock."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Not enough stock available."
    default_code = "insufficient_stock"


class EmptyCart(APIException):
    """Raised when someone tries to check out with an empty cart."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Your cart is empty."
    default_code = "empty_cart"


def custom_exception_handler(exc, context):
    """
    Wrap every API error in one consistent shape:

        {
            "success": false,
            "error": {
                "code": "validation_error",
                "message": "Invalid input.",
                "details": {...}
            }
        }
    """
    response = exception_handler(exc, context)

    # Not a DRF-handled error (e.g. a real bug): let Django return a 500.
    if response is None:
        return None

    data = response.data
    code = getattr(exc, "default_code", "error")

    if isinstance(data, dict) and set(data.keys()) == {"detail"}:
        # Simple errors: 401, 403, 404, 405, custom exceptions...
        message = str(data["detail"])
        details = None
        code = getattr(data["detail"], "code", code)
    else:
        # Validation errors: a dict of field errors or a list of errors.
        message = "Invalid input."
        details = data
        code = "validation_error"

    response.data = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
    return response