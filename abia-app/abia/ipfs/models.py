import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class IPFSDocument(models.Model):
    DOC_TYPES = [
        ('passport', 'Passport'), ('visa', 'Visa'), ('id_card', 'ID Card'),
        ('birth_cert', 'Birth Certificate'), ('medical', 'Medical Record'),
        ('case_file', 'Case File'), ('referral', 'Referral Letter'), ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Upload'), ('pinned', 'Pinned on IPFS'),
        ('failed', 'Upload Failed'), ('removed', 'Removed from IPFS'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=50, choices=DOC_TYPES)
    description = models.TextField(blank=True)
    cid = models.CharField(max_length=128, blank=True, db_index=True)
    ipfs_gateway_url = models.URLField(blank=True)
    pin_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_size = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=128, blank=True)
    local_file = models.FileField(upload_to='ipfs_backups/%Y/%m/', blank=True, null=True)
    migrant = models.ForeignKey('migrants.Migrant', on_delete=models.CASCADE, related_name='ipfs_documents', null=True, blank=True)
    case = models.ForeignKey('cases.Case', on_delete=models.CASCADE, related_name='ipfs_documents', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"{self.title} ({self.doc_type}) - {self.pin_status}"

class PinQueue(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'), ('processing', 'Processing'),
        ('completed', 'Completed'), ('failed', 'Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.OneToOneField(IPFSDocument, on_delete=models.CASCADE, related_name='pin_queue')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    attempts = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['created_at']
    def __str__(self):
        return f"PinQueue {self.document.title} - {self.status}"
