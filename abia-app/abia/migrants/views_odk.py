"""ODK webhook endpoints."""

from typing import Any

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common.exceptions import AbiaBaseException

from .odk_bridge import process_odk_submission


@api_view(["POST"])
@permission_classes([AllowAny])
def odk_webhook(request: Any) -> Response:
    """Receive ODK Central webhook submission."""
    try:
        result = process_odk_submission(request.data)
        return Response(
            {"status": "success", "data": {"id": str(result.id)}},
            status=status.HTTP_201_CREATED,
        )
    except AbiaBaseException as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": f"Internal error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
