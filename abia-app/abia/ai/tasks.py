from celery import shared_task
import random
from .models import AIModel, RiskAssessment, PredictionLog


@shared_task(bind=True, max_retries=3)
def run_risk_prediction(self, migrant_id, model_id=None):
    """Async risk prediction task."""
    try:
        risk_score = round(random.uniform(0.0, 1.0), 3)
        risk_level = 'low' if risk_score < 0.25 else 'medium' if risk_score < 0.5 else 'high' if risk_score < 0.75 else 'critical'
        
        assessment = RiskAssessment.objects.create(
            migrant_id=migrant_id,
            ai_model_id=model_id,
            risk_score=risk_score,
            risk_level=risk_level,
            factors={'async': True, 'task_id': str(self.request.id)},
            recommendations='Async review recommended.' if risk_level in ['high', 'critical'] else 'Routine monitoring.'
        )
        
        PredictionLog.objects.create(
            ai_model_id=model_id,
            input_data={'migrant_id': str(migrant_id), 'model_id': str(model_id)},
            output_data={'risk_score': risk_score, 'risk_level': risk_level},
            confidence=round(random.uniform(0.7, 0.99), 3),
            latency_ms=random.randint(50, 500),
            success=True
        )
        return {'assessment_id': str(assessment.id), 'risk_level': risk_level}
    except Exception as exc:
        PredictionLog.objects.create(
            ai_model_id=model_id,
            input_data={'migrant_id': str(migrant_id)},
            success=False,
            error_message=str(exc)
        )
        raise self.retry(exc=exc, countdown=60)


@shared_task
def batch_predict_all_migrants():
    """Run risk prediction on all active migrants without assessments."""
    from abia.migrants.models import Migrant
    migrants = Migrant.objects.filter(status='active').exclude(risk_assessments__isnull=False)
    count = 0
    for migrant in migrants[:100]:  # Limit batch size
        run_risk_prediction.delay(str(migrant.id))
        count += 1
    return f"Queued {count} predictions"
