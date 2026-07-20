import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChartDashboard(models.Model):
    CHART_TYPES = [
        ("bar", "Bar Chart"),
        ("line", "Line Chart"),
        ("pie", "Pie Chart"),
        ("doughnut", "Doughnut Chart"),
        ("radar", "Radar Chart"),
        ("geo", "Geo Map"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    data_source = models.CharField(max_length=50, help_text="e.g. migrants, cases, referrals")
    query_config = models.JSONField(default=dict, help_text="filter, group_by, aggregation")
    chart_config = models.JSONField(default=dict, blank=True, help_text="Chart.js configuration")
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name