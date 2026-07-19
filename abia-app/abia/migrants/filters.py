"""
ABIA Migration Observatory — Migrants API Filters
"""

import django_filters
from abia.migrants.models import Migrant


class MigrantFilter(django_filters.FilterSet):
    """Advanced filtering for migrants."""
    name_contains = django_filters.CharFilter(field_name="full_name", lookup_expr="icontains")
    phone_contains = django_filters.CharFilter(field_name="phone", lookup_expr="icontains")
    created_after = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Migrant
        fields = ["status", "gender", "nationality", "current_lga"]
