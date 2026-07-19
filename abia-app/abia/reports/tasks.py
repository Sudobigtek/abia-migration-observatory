from celery import shared_task
import csv
import json
import os
from django.utils import timezone
from .models import GeneratedReport

@shared_task
def generate_report_task(report_id):
    """Generate a report file (PDF/Excel/CSV)."""
    try:
        report = GeneratedReport.objects.select_related('template').get(id=report_id)
        report.status = 'generating'
        report.started_at = timezone.now()
        report.save()

        if report.format == 'csv':
            output_path = f"/tmp/report_{report_id}.csv"
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Field', 'Value'])
                writer.writerow(['Report Name', report.name])
                writer.writerow(['Template', report.template.name])
                writer.writerow(['Generated At', str(timezone.now())])
                writer.writerow(['Parameters', json.dumps(report.parameters)])
            report.file_path = output_path
            report.file_size = os.path.getsize(output_path)

        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()
        return {'status': 'completed', 'report_id': report_id}

    except Exception as e:
        report.status = 'failed'
        report.error_message = str(e)[:500]
        report.save()
        return {'status': 'failed', 'error': str(e)}
