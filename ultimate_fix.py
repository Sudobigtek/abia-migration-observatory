#!/usr/bin/env python3
"""
ABIA MIGRATION OBSERVATORY — ULTIMATE FIX SCRIPT v3
Handles: Unicode curly quotes, duplicate Django apps, permissions, migrations, dependencies
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path("/home/abia/abia-migration-observatory/abia-app")

def run_cmd(cmd, cwd=None, timeout=60):
    """Run a shell command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, 
                               cwd=cwd or PROJECT_ROOT, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def fix_broken_files():
    """Fix the 3 known broken files by rewriting them completely."""
    print("🔧 STEP 1: Rewriting broken files with correct syntax...")

    # File 1: fix_created_by.py
    file1 = PROJECT_ROOT / "fix_created_by.py"
    if file1.exists():
        content1 = 