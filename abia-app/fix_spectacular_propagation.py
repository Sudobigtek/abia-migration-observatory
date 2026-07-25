import os, re

def read(p):
    with open(p) as f:
        return f.read()

def write(p, c):
    with open(p, "w") as f:
        f.write(c)
    print("  FIXED:", p)

# Files with @api_view + @extend_schema that need propagation
files = [
    "abia/common/views.py",
    "abia/common/gateway.py",
    "abia/analytics/views.py",
    "abia/audit/views.py",
    "abia/backup/views.py",
    "abia/cbn/views.py",
    "abia/charts/views.py",
    "abia/webhooks/views.py",
    "abia/worldbank/views.py",
    "abia/wto/views.py",
    "abia/throttle/views.py",
    "abia/tenant/views.py",
    "abia/sports/views.py",
    "abia/search/views.py",
    "abia/reports/views.py",
    "abia/quality/views.py",
    "abia/notifications/views.py",
    "abia/ecowas/views.py",
    "abia/geo/views.py",
    "abia/hotspot/views.py",
    "abia/importers/views.py",
    "abia/ncfrmi/views.py",
    "abia/maps/views.py",
    "abia/cases/search.py",
]

for path in files:
    if not os.path.exists(path):
        continue
    
    c = read(path)
    
    # Find all function names that have both @extend_schema and @api_view
    func_names = []
    lines = c.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("def ") and "(" in line:
            func_name = line.strip().split("def ")[1].split("(")[0]
            # Check if this function has @extend_schema before it
            has_extend = False
            has_api_view = False
            for j in range(max(0, i-10), i):
                if "@extend_schema" in lines[j]:
                    has_extend = True
                if "@api_view" in lines[j]:
                    has_api_view = True
            if has_extend and has_api_view:
                func_names.append(func_name)
    
    if func_names:
        # Add propagation block at end of file
        propagation = "\n\n# Propagate _spectacular metadata for drf-spectacular\n"
        for fn in func_names:
            propagation += f"""if hasattr({fn}, '_spectacular') and hasattr({fn}, 'cls'):
    {fn}.cls._spectacular = {fn}._spectacular
"""
        if "# Propagate _spectacular" not in c:
            c = c.rstrip() + "\n" + propagation
            write(path, c)

print("\nDone. Run: python3 manage.py check && python3 manage.py spectacular --file /tmp/schema.yml --validate 2>&1 | tail -5")
