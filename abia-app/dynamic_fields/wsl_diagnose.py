#!/usr/bin/env python3
"""WSL Host Diagnostic — Inspects repository files directly without Docker.

Since Docker is not accessible, we parse the .py files to find
actual method names and model fields.
"""

import ast
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_methods_in_file(filepath, class_name):
    """Parse a Python file and extract method names from a class."""
    try:
        with open(filepath, "r") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith("_"):
                            methods.append(item.name)
                        elif item.name.startswith("__") and item.name.endswith("__"):
                            methods.append(item.name)  # dunder methods
                return methods
        return []
    except FileNotFoundError:
        return [f"FILE NOT FOUND: {filepath}"]
    except Exception as e:
        return [f"ERROR: {e}"]


def find_model_fields(filepath):
    """Parse a models.py and extract field names."""
    try:
        with open(filepath, "r") as f:
            tree = ast.parse(f.read())

        fields = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # Check if value is a model field call
                        if isinstance(node.value, ast.Call):
                            func = node.value.func
                            if isinstance(func, ast.Attribute):
                                if "Field" in func.attr or func.attr in [
                                    "ForeignKey",
                                    "OneToOneField",
                                    "ManyToManyField",
                                ]:
                                    fields.append(target.id)
                            elif isinstance(func, ast.Name):
                                if "Field" in func.id or func.id in [
                                    "ForeignKey",
                                    "OneToOneField",
                                    "ManyToManyField",
                                ]:
                                    fields.append(target.id)
        return fields
    except FileNotFoundError:
        return [f"FILE NOT FOUND: {filepath}"]
    except Exception as e:
        return [f"ERROR: {e}"]


print("=" * 70)
print("WSL HOST DIAGNOSTIC — File-based inspection (no Docker needed)")
print("=" * 70)
print(f"Project root: {PROJECT_ROOT}")
print()

# Check repository files
repos = [
    ("accounts/repositories.py", "LGARepository"),
    ("accounts/repositories.py", "UserRepository"),
    ("migrants/repositories.py", "MigrantRepository"),
    ("cases/repositories.py", "CaseRepository"),
    ("referrals/repositories.py", "ReferralRepository"),
]

print("REPOSITORY METHODS:")
print("-" * 70)
for filepath, class_name in repos:
    full_path = os.path.join(PROJECT_ROOT, filepath)
    methods = find_methods_in_file(full_path, class_name)
    print(f"\n{filepath}::{class_name}")
    if (
        isinstance(methods, list)
        and methods
        and isinstance(methods[0], str)
        and methods[0].startswith(("FILE", "ERROR"))
    ):
        print(f"  {methods[0]}")
    else:
        for m in methods:
            print(f"  - {m}")

# Check model files
models = [
    "accounts/models.py",
    "migrants/models.py",
    "cases/models.py",
    "referrals/models.py",
]

print("\n" + "=" * 70)
print("MODEL FIELDS (best-effort parsing):")
print("-" * 70)
for filepath in models:
    full_path = os.path.join(PROJECT_ROOT, filepath)
    print(f"\n{filepath}")
    if os.path.exists(full_path):
        # Simple line-based parsing for field definitions
        with open(full_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            stripped = line.strip()
            if (
                "=" in stripped
                and not stripped.startswith("#")
                and not stripped.startswith("class")
                and not stripped.startswith("def")
            ):
                if any(
                    field_type in stripped
                    for field_type in [
                        "models.",
                        "Field",
                        "Key",
                        "CharField",
                        "IntegerField",
                        "UUIDField",
                        "DateField",
                        "DateTimeField",
                        "TextField",
                        "EmailField",
                        "BooleanField",
                        "ForeignKey",
                    ]
                ):
                    print(f"  {stripped}")
    else:
        print(f"  FILE NOT FOUND")

# Check test files
print("\n" + "=" * 70)
print("TEST FILES:")
print("-" * 70)
test_dirs = ["accounts/tests", "migrants/tests", "cases/tests", "referrals/tests"]
for td in test_dirs:
    full_td = os.path.join(PROJECT_ROOT, td)
    print(f"\n{td}/")
    if os.path.exists(full_td):
        files = [f for f in os.listdir(full_td) if f.endswith(".py")]
        if files:
            for f in files:
                print(f"  ✅ {f}")
        else:
            print(f"  ⚠️  No .py files")
    else:
        print(f"  ❌ Directory does not exist")

# Check common/exceptions.py
print("\n" + "=" * 70)
print("COMMON MODULES:")
print("-" * 70)
common_files = ["common/exceptions.py", "common/permissions.py", "common/__init__.py"]
for cf in common_files:
    full_cf = os.path.join(PROJECT_ROOT, cf)
    if os.path.exists(full_cf):
        print(f"  ✅ {cf}")
    else:
        print(f"  ❌ {cf} — MISSING")

print("\n" + "=" * 70)
