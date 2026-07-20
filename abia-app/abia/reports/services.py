import csv
import io
from datetime import datetime
from django.db.models import Count, Avg
from .models import GeneratedReport

class ReportService:
    @staticmethod
    def generate_migrant_report(params):
        from abia.migrants.models import Migrant
        qs = Migrant.objects.all()
        lga = params.get("lga")
        status = params.get("status")
        if lga:
            qs = qs.filter(current_lga_id=lga)
        if status:
            qs = qs.filter(status=status)
        data = {
            "total": qs.count(),
            "by_gender": list(qs.values("gender").annotate(count=Count("id")).values("gender", "count")),
            "by_status": list(qs.values("status").annotate(count=Count("id")).values("status", "count")),
            "by_lga": list(qs.values("current_lga__name").annotate(count=Count("id")).values("current_lga__name", "count")[:20]),
            "recent": list(qs.order_by("-created_at").values("full_name", "status", "created_at")[:10]),
        }
        return data

    @staticmethod
    def generate_case_report(params):
        from abia.cases.models import Case
        qs = Case.objects.all()
        lga = params.get("lga")
        case_type = params.get("case_type")
        if lga:
            qs = qs.filter(current_lga_id=lga)
        if case_type:
            qs = qs.filter(case_type=case_type)
        data = {
            "total": qs.count(),
            "open": qs.filter(status="open").count(),
            "resolved": qs.filter(status="resolved").count(),
            "by_type": list(qs.values("case_type").annotate(count=Count("id")).values("case_type", "count")),
            "by_priority": list(qs.values("priority").annotate(count=Count("id")).values("priority", "count")),
        }
        return data

    @staticmethod
    def export_to_csv(data, headers):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    def build_report(template, params, user):
        report = GeneratedReport.objects.create(
            template=template,
            title=params.get("title", template.name),
            parameters=params,
            generated_by=user,
            status="generating"
        )
        try:
            if template.report_type == "migrants":
                data = ReportService.generate_migrant_report(params)
            elif template.report_type == "cases":
                data = ReportService.generate_case_report(params)
            else:
                data = {"message": "Custom report type not yet implemented"}
            report.data = data
            report.status = "completed"
            report.save()
            return report
        except Exception as e:
            report.status = "failed"
            report.error_message = str(e)[:500]
            report.save()
            return report