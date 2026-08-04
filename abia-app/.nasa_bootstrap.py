import os, sys, re, json, shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE = Path('/home/abia/abia-migration-observatory/abia-app')
os.chdir(BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abia.settings.development')
sys.path.insert(0, str(BASE))
import django
django.setup()
