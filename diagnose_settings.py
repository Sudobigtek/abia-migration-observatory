#!/usr/bin/env python3
"""
Diagnose settings.py syntax errors
"""

SETTINGS = "/home/abia/abia-migration-observatory/abia-app/abia/settings.py"

with open(SETTINGS, "r") as f:
    lines = f.readlines()

print("=== SETTINGS.PY LINES 115-125 ===")
for i, line in enumerate(lines[114:125], start=115):
    marker = "  <<< BROKEN" if "'" in line and line.count("'") % 2 != 0 else ""
    print(f"{i:3d}: {line.rstrip()}{marker}")

print("\n=== ALL LINES WITH ODD QUOTE COUNT ===")
for i, line in enumerate(lines, start=1):
    if "'" in line and line.count("'") % 2 != 0:
        print(f"{i:3d}: {line.rstrip()}")
