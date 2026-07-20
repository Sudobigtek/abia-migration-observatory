from datetime import datetime
from .models import DataQualityRule, DataQualityIssue

class QualityService:
    @staticmethod
    def check_completeness(entity, field_name):
        value = getattr(entity, field_name, None)
        return value is not None and str(value).strip() != ""

    @staticmethod
    def check_uniqueness(model_class, field_name, value, exclude_id=None):
        qs = model_class.objects.filter(**{field_name: value})
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.count() == 0

    @staticmethod
    def run_rules(entity_type, entity):
        rules = DataQualityRule.objects.filter(entity_type=entity_type, is_active=True)
        issues = []
        for rule in rules:
            passed = True
            if rule.condition == "not_null":
                passed = QualityService.check_completeness(entity, rule.field_name)
            elif rule.condition == "unique":
                value = getattr(entity, rule.field_name, None)
                model_class = entity.__class__
                passed = QualityService.check_uniqueness(model_class, rule.field_name, value, entity.id)

            if not passed:
                issue, _ = DataQualityIssue.objects.get_or_create(
                    rule=rule,
                    entity_type=entity_type,
                    entity_id=str(entity.id),
                    field_name=rule.field_name,
                    defaults={
                        "issue_description": f"{rule.name} failed for {rule.field_name}",
                        "severity": rule.severity,
                    }
                )
                issues.append(issue)
        return issues

    @staticmethod
    def run_all_checks():
        from abia.migrants.models import Migrant
        from abia.cases.models import Case
        total_issues = 0
        for m in Migrant.objects.all():
            issues = QualityService.run_rules("migrants.Migrant", m)
            total_issues += len(issues)
        for c in Case.objects.all():
            issues = QualityService.run_rules("cases.Case", c)
            total_issues += len(issues)
        return total_issues

    @staticmethod
    def get_quality_score(entity_type):
        from django.db.models import Count
        total = DataQualityIssue.objects.filter(entity_type=entity_type).count()
        open_issues = DataQualityIssue.objects.filter(entity_type=entity_type, status="open").count()
        if total == 0:
            return 100.0
        return round((1 - open_issues / total) * 100, 2)