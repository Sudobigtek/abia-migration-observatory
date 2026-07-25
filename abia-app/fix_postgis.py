import os

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# Fix cases/serializers.py
csp = "abia/cases/serializers.py"
if os.path.exists(csp):
    c = read(csp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "def get_location(self, obj)" in c:
        before = c.split("def get_location(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before:
            c = c.replace(
                "def get_location(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point or null"))\n    def get_location(self, obj)'
            )
    write(csp, c)

# Fix migrants/serializers.py
msp = "abia/migrants/serializers.py"
if os.path.exists(msp):
    c = read(msp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "def get_location(self, obj)" in c:
        before = c.split("def get_location(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before:
            c = c.replace(
                "def get_location(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point or null"))\n    def get_location(self, obj)'
            )
    if "def get_gps_coordinates(self, obj)" in c:
        before = c.split("def get_gps_coordinates(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before:
            c = c.replace(
                "def get_gps_coordinates(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Point or null"))\n    def get_gps_coordinates(self, obj)'
            )
    write(msp, c)

# Fix accounts/serializers.py
asp = "abia/accounts/serializers.py"
if os.path.exists(asp):
    c = read(asp)
    if "from drf_spectacular.utils import extend_schema_field" not in c:
        c = "from drf_spectacular.utils import extend_schema_field\n" + c
    if "def get_boundary(self, obj)" in c:
        before = c.split("def get_boundary(self, obj)")[0].rsplit("def ", 1)[-1]
        if "@extend_schema_field" not in before:
            c = c.replace(
                "def get_boundary(self, obj)",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Polygon or null"))\n    def get_boundary(self, obj)'
            )
    elif "boundary" in c and "class Meta:" in c:
        # If boundary is a model field, add explicit serializer field
        if "boundary = serializers" not in c:
            c = c.replace(
                "class Meta:",
                "boundary = serializers.SerializerMethodField()\n\n    class Meta:"
            )
            c = c.replace(
                "def get_boundary(self, obj):",
                '@extend_schema_field(serializers.DictField(help_text="GeoJSON Polygon or null"))\n    def get_boundary(self, obj):'
            )
    write(asp, c)

print("\nDone.")
