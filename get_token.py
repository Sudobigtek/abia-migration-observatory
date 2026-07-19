#!/usr/bin/env python3
"""
Generate DRF auth token for abiaadmin
"""

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings')
sys.path.insert(0, '/home/abia/abia-migration-observatory/abia-app')

import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

user = User.objects.get(username='abiaadmin')
token, created = Token.objects.get_or_create(user=user)

print("=" * 65)
print("  AUTH TOKEN GENERATED")
print("=" * 65)
print()
print(f"  Username: {user.username}")
print(f"  Token:    {token.key}")
print()
print("  Use this in your API requests:")
print('    curl -H "Authorization: Token ' + token.key + '" http://127.0.0.1:8000/api/v1/migrants/')
print()
