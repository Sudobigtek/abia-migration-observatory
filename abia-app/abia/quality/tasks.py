from celery import shared_task
from django.db.models import Q
from .models import DataQualityRule, DataQualityIssue

@shared_task
def run_data_quality_scan():
    """Run all active quality rules and create issues."""
    rules = DataQualityRule.objects.filter(is_active=True)
    total_created = 0

    for rule in rules:
        if rule.model_name == 'migrants.Migrant':
            from abia.migrants.models import Migrant
            if rule.rule_type == 'required_field' and rule.field_name:
                empty_records = Migrant.objects.filter(
                    Q(**{f"{rule.field_name}__isnull": True}) |
                    Q(**{f"{rule.field_name}": ''})
                )
                for record in empty_records:
                    issue, created = DataQualityIssue.objects.get_or_create(
                        rule=rule,
                        record_id=record.id,
                        defaults={
                            'model_name': rule.model_name,
                            'field_name': rule.field_name,
                            'issue_description': f"Required field '{rule.field_name}' is empty",
                        }
                    )
                    if created:
                        total_created += 1

            elif rule.rule_type == 'duplicate' and rule.field_name:
                from django.db.models import Count
                duplicates = Migrant.objects.values(rule.field_name).annotate(
                    count=Count('id')
                ).filter(count__gt=1)
                for dup in duplicates:
                    records = Migrant.objects.filter(**{rule.field_name: dup[rule.field_name]})
                    for record in records[1:]:
                        issue, created = DataQualityIssue.objects.get_or_create(
                            rule=rule,
                            record_id=record.id,
                            defaults={
                                'model_name': rule.model_name,
                                'field_name': rule.field_name,
                                'issue_description': f"Duplicate value for '{rule.field_name}': {dup[rule.field_name]}",
                                'current_value': str(dup[rule.field_name]),
                            }
                        )
                        if created:
                            total_created += 1

    return {'status': 'completed', 'issues_created': total_created}
