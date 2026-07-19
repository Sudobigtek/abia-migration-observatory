from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from abia.common.exceptions import (
    DuplicateSubmissionError,
    InvalidGPSDataError,
    LGANotFoundError,
)

from .odk_bridge import ODKBridge


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def odk_webhook(request):
    try:
        migrant = ODKBridge.process_submission(request.data, request.user)
        return Response(
            {"status": "success", "migrant_id": str(migrant.id)}, status=201
        )
    except DuplicateSubmissionError as e:
        return Response({"status": "duplicate", "message": str(e)}, status=409)
    except (LGANotFoundError, InvalidGPSDataError) as e:
        return Response({"status": "error", "message": str(e)}, status=422)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
