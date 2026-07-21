#!/usr/bin/env python3
import os, stat

APP = "/home/abia/abia-migration-observatory/abia-app"
CORE = "/home/abia/abia-migration-observatory/abia-core"

def wf(path, content):
    if path.startswith("abia/") or path.startswith("templates/"):
        full = os.path.join(APP, path)
    else:
        full = os.path.join(CORE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"OK: {path}")

print("=" * 60)
print("PHASE E: NCFRMI/GIZ Report UI Templates")
print("=" * 60)
