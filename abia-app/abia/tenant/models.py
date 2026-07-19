from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TenantRole(models.Model):
    ROLE_CHOICES = [
        ("field_officer", "Field Officer"),
        ("lga_coordinator", "LGA Coordinator"),
        ("state_admin", "State Administrator"),
        ("super_admin", "Super Admin"),
        ("partner_viewer", "Partner Viewer"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tenant_role")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="field_officer")
    lga = models.ForeignKey("accounts.LGA", on_delete=models.SET_NULL, null=True, blank=True)
    can_access_all_lgas = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.role}"

    def can_access_lga(self, lga_id):
        if self.role in ["state_admin", "super_admin"] or self.can_access_all_lgas:
            return True
        return self.lga_id == lga_id

    def get_visible_lgas(self):
        from accounts.models import LGA
        if self.role in ["state_admin", "super_admin"] or self.can_access_all_lgas:
            return LGA.objects.all()
        if self.lga:
            return LGA.objects.filter(id=self.lga_id)
        return LGA.objects.none()