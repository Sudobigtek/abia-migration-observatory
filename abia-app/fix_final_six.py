import os, re

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# =====================================================================
# 1. Fix reports/views.py generate_report
# =====================================================================
rp = "abia/reports/views.py"
if os.path.exists(rp):
    c = read(rp)
    # Ensure decorator exists and is correct
    if "def generate_report(request):" in c:
        if "@extend_schema" not in c.split("def generate_report(request):")[0].rsplit("def ", 1)[-1]:
            c = c.replace(
                "def generate_report(request):",
                '@extend_schema(\n    responses=GenerateReportResponse,\n    tags=["Reports"],\n    summary="Generate report",\n)\ndef generate_report(request):'
            )
        # Force serializer_class on the wrapper
        if "generate_report.cls.serializer_class" not in c:
            c = c.rstrip() + "\n\ngenerate_report.cls.serializer_class = GenerateReportResponse\n"
        write(rp, c)

# =====================================================================
# 2. Fix cases/serializers.py - CaseDetailSerializer location field
# =====================================================================
csp = "abia/cases/serializers.py"
if os.path.exists(csp):
    c = read(csp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    # Find CaseDetailSerializer and add explicit location field
    if "class CaseDetailSerializer" in c:
        parts = c.split("class CaseDetailSerializer")
        before = parts[0]
        rest = parts[1]
        # Add location = serializers.SerializerMethodField() before class Meta in CaseDetailSerializer
        if "location = serializers.SerializerMethodField()" not in rest.split("class Meta:")[0]:
            rest = rest.replace(
                "class Meta:",
                "location = serializers.SerializerMethodField()\n\n    class Meta:",
                1
            )
        c = before + "class CaseDetailSerializer" + rest
    # Add extend_schema_field to get_location
    if "def get_location(self, obj)" in c:
        before_getter = c.split("def get_location(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before_getter:
            c = c.replace(
                "def get_location(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point or null"))\n    def get_location(self, obj)'
            )
    write(csp, c)

# =====================================================================
# 3. Fix migrants/serializers.py - MigrantDetailSerializer
# =====================================================================
msp = "abia/migrants/serializers.py"
if os.path.exists(msp):
    c = read(msp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "class MigrantDetailSerializer" in c:
        parts = c.split("class MigrantDetailSerializer")
        before = parts[0]
        rest = parts[1]
        # Add explicit fields before class Meta
        meta_split = rest.split("class Meta:", 1)
        class_body = meta_split[0]
        meta_and_after = "class Meta:" + meta_split[1] if len(meta_split) > 1 else ""
        if "location = serializers" not in class_body:
            class_body = "location = serializers.SerializerMethodField()\n    gps_coordinates = serializers.SerializerMethodField()\n\n    " + class_body.lstrip()
        rest = class_body + meta_and_after
        c = before + "class MigrantDetailSerializer" + rest
    # Add extend_schema_field to getters
    if "def get_location(self, obj)" in c:
        before_getter = c.split("def get_location(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before_getter:
            c = c.replace(
                "def get_location(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point or null"))\n    def get_location(self, obj)'
            )
    if "def get_gps_coordinates(self, obj)" in c:
        before_getter = c.split("def get_gps_coordinates(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before_getter:
            c = c.replace(
                "def get_gps_coordinates(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point or null"))\n    def get_gps_coordinates(self, obj)'
            )
    write(msp, c)

# =====================================================================
# 4. Fix accounts/serializers.py - LGASerializer boundary field
# =====================================================================
asp = "abia/accounts/serializers.py"
if os.path.exists(asp):
    c = read(asp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "class LGASerializer" in c:
        parts = c.split("class LGASerializer")
        before = parts[0]
        rest = parts[1]
        if "boundary = serializers" not in rest.split("class Meta:")[0]:
            rest = rest.replace(
                "class Meta:",
                "boundary = serializers.SerializerMethodField()\n\n    class Meta:",
                1
            )
        c = before + "class LGASerializer" + rest
    if "def get_boundary(self, obj)" in c:
        before_getter = c.split("def get_boundary(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before_getter:
            c = c.replace(
                "def get_boundary(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Polygon or null"))\n    def get_boundary(self, obj)'
            )
    write(asp, c)

print("\nDone. Run: python3 manage.py check && python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -5")
