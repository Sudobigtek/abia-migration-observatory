from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FormSubmission(models.Model):
    FORM_TYPES = [
        ('migration', 'Migration Data'),
        ('trade', 'Trade & Commerce'),
        ('sports', 'Sports & Youth'),
        ('hotspot', 'Hotspot Monitoring'),
        ('returnee', 'Returnee Assessment'),
        ('general', 'General Data'),
    ]
    
    form_type = models.CharField(max_length=20, choices=FORM_TYPES, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    data = models.JSONField(default=dict)
    submitted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    ipfs_hash = models.CharField(max_length=128, blank=True, db_index=True)
    synced_to_ncfrmi = models.BooleanField(default=False)
    synced_to_iom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['form_type', 'created_at'])]
    
    def __str__(self):
        return f"{self.get_form_type_display()} — {self.created_at.strftime('%Y-%m-%d %H:%M')}"
