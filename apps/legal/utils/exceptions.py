from __future__ import annotations

from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {
                "code": getattr(exc, "default_code", "error"),
                "message": response.data,
            }
        }
    return response
