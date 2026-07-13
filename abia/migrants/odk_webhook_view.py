from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .odk_bridge import process_odk_submission
from .exceptions import DuplicateSubmissionError, LGANotFoundError


`api_view(["POST"])
@permission_classes([IsAuthenticated])
def odk_webhook(request):
    try:
        migrant = process_odk_submission(request.data)
        return Response({"status": "success", "migrant_id": str(migrant.id)}, status=201)
    except DuplicateSubmissionError as e:
        return Response({"status": "duplicate", "message": str(e)}, status=409)
    except LGANotFoundError as e:
        return Response({"status": "error", "message": str(e)}, status=422)
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)
