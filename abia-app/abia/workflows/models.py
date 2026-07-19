import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WorkflowDefinition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    model_name = models.CharField(max_length=100, help_text="e.g., 'cases.Case'")
    steps = models.JSONField(default=list, help_text="Ordered list of workflow steps")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workflow_definitions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class WorkflowInstance(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name='instances')
    object_type = models.CharField(max_length=100)
    object_id = models.UUIDField()
    current_step = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='workflow_instances')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.workflow.name} - {self.object_type} #{self.object_id}"

class WorkflowStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name='workflow_steps')
    name = models.CharField(max_length=255)
    order = models.PositiveSmallIntegerField()
    action_type = models.CharField(max_length=50, default='manual')
    required_role = models.CharField(max_length=50, blank=True)
    auto_trigger_condition = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
