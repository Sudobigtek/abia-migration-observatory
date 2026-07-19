#!/usr/bin/env python3
"""
Fix DRF authentication to include TokenAuthentication
"""

import os

SETTINGS = "/home/abia/abia-migration-observatory/abia-app/abia/settings.py"

with open(SETTINGS, "r") as f:
    content = f.read()

# Check if TokenAuthentication is already configured
if "TokenAuthentication" in content:
    print("TokenAuthentication already configured")
    exit(0)

# Find the REST_FRAMEWORK block and add TokenAuthentication
if "REST_FRAMEWORK" in content:
    # Add TokenAuthentication to the authentication classes
    if "'rest_framework.authentication.TokenAuthentication'" not in content:
        content = content.replace(
            "'rest_framework.authentication.SessionAuthentication',",
            "'rest_framework.authentication.SessionAuthentication',\n        'rest_framework.authentication.TokenAuthentication',"
        )
        print("Added TokenAuthentication to DRF settings")
    else:
        print("TokenAuthentication already in settings")
else:
    # Add full REST_FRAMEWORK config if missing
    config = """
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
"""
    content = content.rstrip() + "\n\n" + config
    print("Added REST_FRAMEWORK config with TokenAuthentication")

with open(SETTINGS, "w") as f:
    f.write(content)

print("Done. Restart the server.")
