#!/usr/bin/env python3
"""Diagnose repository issues."""

def diagnose():
    """Run diagnostics on accounts repositories."""
    print("--- accounts.repositories ---")
    try:
        from abia.accounts import repositories
        print("OK")
    except ImportError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    diagnose()
