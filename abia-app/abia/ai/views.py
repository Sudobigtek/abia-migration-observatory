from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import RiskAssessment, AIPredictionLog
from .services import assess_migrant_risk
from abia.migrants.models import Migrant
import time
import django.utils.timezone

class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.select_related("migrant", "assessed_by")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from .serializers import RiskAssessmentSerializer
        return RiskAssessmentSerializer

    def perform_create(self, serializer):
        serializer.save(assessed_by=self.request.user)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_assess_migrant(request, migrant_id):
    migrant = get_object_or_404(Migrant, id=migrant_id)
    migrant_data = {
        "full_name": migrant.full_name,
        "gender": migrant.gender,
        "nationality": migrant.nationality,
        "status": migrant.status,
        "current_lga": migrant.current_lga.name if migrant.current_lga else None,
        "case_count": migrant.cases.filter(status__in=["open", "in_progress"]).count(),
        "updated_at": migrant.updated_at.isoformat() if hasattr(migrant, "updated_at") else None,
    }
    start_time = time.time()
    result = assess_migrant_risk(migrant_data)
    latency = int((time.time() - start_time) * 1000)
    AIPredictionLog.objects.create(
        prediction_type="risk_assessment",
        input_data=migrant_data,
        output_data=result,
        confidence=result.get("risk_score"),
        model_used="ollama:llama3",
        latency_ms=latency,
        success="error" not in result
    )
    if "error" in result:
        return Response({
            "status": "ai_error",
            "error": result["error"],
            "migrant_id": str(migrant_id)
        }, status=503)
    assessment = RiskAssessment.objects.create(
        migrant=migrant,
        risk_level=result.get("risk_level", "low"),
        risk_score=result.get("risk_score", 0.0),
        factors=result.get("factors", {}),
        recommendations=result.get("recommendations", []),
        model_version="ollama:llama3",
        raw_response=result,
        assessed_by=request.user
    )
    return Response({
        "status": "assessed",
        "assessment_id": str(assessment.id),
        "risk_level": assessment.risk_level,
        "risk_score": assessment.risk_score,
        "factors": assessment.factors,
        "recommendations": assessment.recommendations,
        "latency_ms": latency
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_health(request):
    from .services import query_ollama
    result = query_ollama("Return JSON: {\"status\": \"ok\"}", model="llama3")
    return Response({
        "ollama_status": "online" if "error" not in result else "offline",
        "response": result,
        "timestamp": django.utils.timezone.now().isoformat()
    })
