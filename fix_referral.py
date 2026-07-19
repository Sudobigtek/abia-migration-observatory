#!/usr/bin/env python3
"""
Fix: Create the test referral using actual Case instances (not dicts).
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings')
sys.path.insert(0, '/home/abia/abia-migration-observatory/abia-app')

import django
django.setup()

from abia.cases.models import Case
from abia.referrals.models import Referral
from abia.accounts.models import LGA
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='abiaadmin')
lga = LGA.objects.get(code='ABA')
lga2 = LGA.objects.get(code='UMU')

# Get the actual Case instances (not dicts)
case1 = Case.objects.get(case_type='irregular_migration', migrant__full_name='Chinedu Okoro')

ref, created = Referral.objects.get_or_create(
    case=case1,
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
print("All test data ready. Refresh http://127.0.0.1:8000/dashboard/")
