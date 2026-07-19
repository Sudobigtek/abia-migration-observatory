import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DocumentCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    allowed_extensions = models.JSONField(default=list, help_text="e.g., ['.pdf', '.jpg']")
    max_file_size_mb = models.PositiveSmallIntegerField(default=10)
    requires_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Document Categories'

    def __str__(self):
        return self.name

class Document(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_size = models.PositiveIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_uploads')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_documents')
    approved_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveSmallIntegerField(default=1)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (v{self.version})"
