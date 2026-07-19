#!/usr/bin/env python3
"""
ABIA Migration Observatory — Create Test Data via Django ORM
Bypasses API auth by using the ORM directly.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings')
sys.path.insert(0, '/home/abia/abia-migration-observatory/abia-app')
django.setup()

from django.contrib.auth import get_user_model
from abia.accounts.models import LGA
from abia.migrants.models import Migrant
from abia.cases.models import Case
from abia.referrals.models import Referral
import uuid

User = get_user_model()

print("=" * 65)
print("  TEST DATA GENERATOR")
print("=" * 65)

# Get or create superuser
try:
    admin = User.objects.get(username='abiaadmin')
    print(f"Using existing user: {admin.username}")
except User.DoesNotExist:
    print("User 'abiaadmin' not found. Please create it first.")
    sys.exit(1)

# Create test LGA if none exist
lga, created = LGA.objects.get_or_create(
    code='ABA',
    defaults={
        'name': 'Aba North',
        'population_2023': 500000,
    }
)
print(f"LGA 'Aba North': {'created' if created else 'exists'}")

lga2, created = LGA.objects.get_or_create(
    code='UMU',
    defaults={
        'name': 'Umuahia',
        'population_2023': 300000,
    }
)
print(f"LGA 'Umuahia': {'created' if created else 'exists'}")

# Create test migrants
migrants_data = [
    {
        'full_name': 'Chinedu Okoro',
        'gender': 'male',
        'phone': '+2348011111111',
        'nationality': 'Nigeria',
        'state_of_origin': 'Abia',
        'current_lga': lga,
        'status': 'active',
    },
    {
        'full_name': 'Ngozi Eze',
        'gender': 'female',
        'phone': '+2348022222222',
        'nationality': 'Nigeria',
        'state_of_origin': 'Imo',
        'current_lga': lga,
        'status': 'active',
    },
    {
        'full_name': 'Emeka Okafor',
        'gender': 'male',
        'phone': '+2348033333333',
        'nationality': 'Nigeria',
        'state_of_origin': 'Anambra',
        'current_lga': lga2,
        'status': 'relocated',
    },
]

created_migrants = []
for data in migrants_data:
    m, created = Migrant.objects.get_or_create(
        full_name=data['full_name'],
        defaults={**data, 'created_by': admin}
    )
    created_migrants.append(m)
    print(f"Migrant '{m.full_name}': {'created' if created else 'exists'}")

# Create test cases
cases_data = [
    {
        'migrant': created_migrants[0],
        'case_type': 'irregular_migration',
        'description': 'Migrant found without proper documentation at border.',
        'status': 'open',
        'priority': 'high',
        'lga': lga,
    },
    {
        'migrant': created_migrants[1],
        'case_type': 'skills_training',
        'description': 'Request for vocational training in tailoring.',
        'status': 'in_progress',
        'priority': 'medium',
        'lga': lga,
        'assigned_to': admin,
    },
    {
        'migrant': created_migrants[2],
        'case_type': 'returnee_reintegration',
        'description': 'Returnee from Libya seeking reintegration support.',
        'status': 'resolved',
        'priority': 'critical',
        'lga': lga2,
    },
]

for data in cases_data:
    c, created = Case.objects.get_or_create(
        migrant=data['migrant'],
        case_type=data['case_type'],
        defaults={**data, 'created_by': admin}
    )
    print(f"Case for '{c.migrant.full_name}' ({c.case_type}): {'created' if created else 'exists'}")

# Create test referral
if len(created_migrants) >= 2:
    ref, created = Referral.objects.get_or_create(
        case=cases_data[0],  # The irregular migration case
        defaults={
            'from_lga': lga,
            'to_lga': lga2,
            'to_organization': 'NCFRMI Abuja',
            'to_contact_name': 'Dr. Bernard Doro',
            'reason': 'Escalation to federal level for documentation support.',
            'status': 'pending',
            'created_by': admin,
        }
    )
    print(f"Referral: {'created' if created else 'exists'}")

print()
print("=" * 65)
print("  TEST DATA CREATED SUCCESSFULLY")
print("=" * 65)
print()
print("  Refresh http://127.0.0.1:8000/dashboard/ to see the data.")
