import re
with open("abia/urls.py") as f: c = f.read()
if "api_metadata" not in c:
    c = c.replace("from django.urls import path", "from django.urls import path\\nfrom abia.common.metadata import api_metadata, health_check")
    c = re.sub(r"(urlpatterns\\s*=\\s*\\[)", r\"\\1\\n    path("\"api/v1/metadata/\"", api_metadata, name="\"api-metadata\""),\\n    path("\"api/v1/health/\"", health_check, name="\"api-health\""),\", c)
    with open("abia/urls.py", "w") as f: f.write(c)
    print("WIRED")
else: print("ALREADY WIRED")
