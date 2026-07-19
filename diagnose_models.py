#!/usr/bin/env python3
"""
ABIA Migration Observatory — Model Diagnostic Script
Extracts all model definitions for API architecture planning.
"""

import os
import ast

APP_DIR = "/home/abia/abia-migration-observatory/abia-app"
APPS = ["cases", "referrals", "accounts", "ai", "ipfs"]

print("=" * 70)
print("  MODEL DIAGNOSTIC REPORT")
print("=" * 70)
print()

for app in APPS:
    models_path = os.path.join(APP_DIR, "abia", app, "models.py")
    print(f"\n{'='*70}")
    print(f"  APP: {app}")
    print(f"  File: {models_path}")
    print(f"{'='*70}")

    if os.path.exists(models_path):
        with open(models_path, "r") as f:
            content = f.read()
        print(content)
    else:
        print("  [FILE NOT FOUND]")
    print()

# Also check for any models in dynamic_fields
df_models = os.path.join(APP_DIR, "dynamic_fields", "models.py")
print(f"\n{'='*70}")
print(f"  APP: dynamic_fields")
print(f"  File: {df_models}")
print(f"{'='*70}")
if os.path.exists(df_models):
    with open(df_models, "r") as f:
        print(f.read())
else:
    print("  [FILE NOT FOUND]")
