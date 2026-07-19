from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.db import models


class LGA(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    boundary = gis_models.MultiPolygonField(srid=4326, null=True, blank=True)
    population_2023 = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "accounts"
        ordering = ["name"]

    def __str__(self):
        return self.name



    @property
    def user_count(self):
        return self.users.count()
    
    @property
    def case_count(self):
        from abia.cases.models import Case
        return Case.objects.filter(migrant__current_lga=self).count()
    
    @property
    def migrant_count(self):
        from abia.migrants.models import Migrant
        return Migrant.objects.filter(current_lga=self).count()

class User(AbstractUser):
    ROLES = [
        ("field_officer", "Field Officer"),
        ("lga_coordinator", "LGA Coordinator"),
        ("state_admin", "State Administrator"),
        ("super_admin", "Super Admin"),
    ]
    phone = models.CharField(max_length=20, blank=True)
    lga = models.ForeignKey(
        LGA, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    role = models.CharField(max_length=20, choices=ROLES, default="field_officer")

    def clean(self):
        from django.core.exceptions import ValidationError

        from abia.common.validators import validate_role

        super().clean()
        if self.role:
            try:
                validate_role(self.role)
            except ValidationError as e:
                raise ValidationError({"role": e.message})

    class Meta:
        app_label = "accounts"

    def __str__(self):
        return f"{self.get_full_name()} ({self.lga})"