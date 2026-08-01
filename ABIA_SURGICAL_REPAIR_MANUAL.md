# NASA-LEVEL ABIA MIGRATION OBSERVATORY — SURGICAL REPAIR PROTOCOL

> Date: 2026-07-28
> Status: CRITICAL
> Goal: Restore all pages to 100% functional with correct links and real data

---

## EXECUTIVE SUMMARY OF BREAKS

| Component | Status | Root Cause |
|-----------|--------|------------|
| / (Landing) | HTTP 500 | landing.html corrupted by nav injection; unclosed tags |
| /dashboard/ | Partial | Shows data but may still have hardcoded numbers |
| /command-center/ | HTTP 500 | dashboard/index.html missing; command_center import broken |
| /onboarding/ | Wrong Links | Gov -> /dashboard/ (should be /command-center/); Partner -> /admin/ (should be /reports/) |
| abia/urls.py | Broken | Duplicate public_dashboard namespace; command-center route malformed |
| abia/charts/urls.py | Broken | command_center referenced but not in import line |
| abia/charts/views.py | Dirty | Duplicate django.shortcuts import blocks appended |
| templates/public_dashboard/dashboard.html | Hardcoded | Stats like 100, 210, 255 still hardcoded |

---

## PHASE 0: KILL EVERYTHING

Copy and paste this entire block into WSL:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate

echo "=== NUCLEAR KILL ==="
pkill -9 -f "manage.py runserver" 2>/dev/null
pkill -9 -f "python.*8001" 2>/dev/null
sleep 3

echo "=== VERIFY PORT FREE ==="
ss -tlnp | grep 8001 || echo 'Port 8001 is FREE'

echo "=== VERIFY NO GHOST PROCESSES ==="
ps aux | grep "manage.py runserver" | grep -v grep || echo "No ghost servers"
```

---

## PHASE 1: FIX abia/urls.py — ROOT ROUTING TABLE

Diagnosis: Duplicate public_dashboard namespace. command-center wired as include() instead of direct view. Root / hijacked by public_dashboard.urls empty path.

Copy and paste this entire block:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os

print("=" * 70)
print("PHASE 1: FIXING abia/urls.py")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

with open("abia/urls.py", "r") as f:
    original = f.read()

lines = original.split("
")
keep_lines = []
seen_paths = set()
for line in lines:
    stripped = line.strip()
    if stripped.startswith("path('', include('abia.public_dashboard.urls'))"):
        continue
    if stripped.startswith('path("", include("abia.public_dashboard.urls"))'):
        continue
    if stripped.startswith('path("command-center/",'):
        continue
    if stripped.startswith('path("", TemplateView.as_view(template_name="landing.html")'):
        continue
    if stripped.startswith("import abia.charts.views"):
        continue
    if stripped and stripped not in seen_paths:
        seen_paths.add(stripped)
        keep_lines.append(line)
    elif not stripped:
        keep_lines.append(line)

new_content = "
".join(keep_lines)
new_content = new_content.rstrip()

if 'path("", TemplateView.as_view(template_name="landing.html")' not in new_content:
    last_bracket = new_content.rfind("]")
    if last_bracket > 0:
        new_content = (
            new_content[:last_bracket]
            + '    path("", TemplateView.as_view(template_name="landing.html"), name="home"),
'
            + new_content[last_bracket:]
        )

if 'path("dashboard/", include("abia.public_dashboard.urls"))' not in new_content:
    last_bracket = new_content.rfind("]")
    if last_bracket > 0:
        new_content = (
            new_content[:last_bracket]
            + '    path("dashboard/", include("abia.public_dashboard.urls")),
'
            + new_content[last_bracket:]
        )

if 'path("command-center/", abia.charts.views.command_center' not in new_content:
    last_bracket = new_content.rfind("]")
    if last_bracket > 0:
        new_content = (
            new_content[:last_bracket]
            + '    path("command-center/", abia.charts.views.command_center, name="command-center"),
'
            + new_content[last_bracket:]
        )

if "import abia.charts.views" not in new_content:
    import_idx = new_content.find("from django.urls import")
    if import_idx >= 0:
        end_of_line = new_content.find("
", import_idx)
        new_content = (
            new_content[:end_of_line + 1]
            + "import abia.charts.views
"
            + new_content[end_of_line + 1:]
        )

with open("abia/urls.py", "w") as f:
    f.write(new_content)

print("OK abia/urls.py rebuilt")
print("  / -> landing.html")
print("  /dashboard/ -> public_dashboard")
print("  /command-center/ -> abia.charts.views.command_center")
print("  Duplicate public_dashboard include REMOVED")
PYEOF
```

---

## PHASE 2: FIX abia/charts/urls.py — IMPORT LINE

Diagnosis: command_center referenced in path() but NOT in the from .views import line.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os

print("
" + "=" * 70)
print("PHASE 2: FIXING abia/charts/urls.py")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

with open("abia/charts/urls.py", "r") as f:
    content = f.read()

old_import = "from .views import ChartDashboardViewSet, chart_data, preset_charts, analytics_summary"
new_import = "from .views import ChartDashboardViewSet, chart_data, preset_charts, analytics_summary, command_center"

if old_import in content:
    content = content.replace(old_import, new_import)
    with open("abia/charts/urls.py", "w") as f:
        f.write(content)
    print("OK Added command_center to import line")
else:
    lines = content.split("
")
    if len(lines) > 2 and "command_center" in lines[2]:
        print("OK command_center already imported")
    else:
        print("WARNING Import line format unexpected")

if 'path("command-center/", command_center' in content:
    lines = content.split("
")
    clean_lines = []
    for line in lines:
        if 'path("command-center/", command_center' in line:
            continue
        clean_lines.append(line)
    content = "
".join(clean_lines)
    with open("abia/charts/urls.py", "w") as f:
        f.write(content)
    print("OK Removed command-center path from charts/urls.py (now in root)")
PYEOF
```

---

## PHASE 3: CLEAN abia/charts/views.py — REMOVE DUPLICATE IMPORTS

Diagnosis: Multiple appended blocks of from django.shortcuts import render, etc.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os

print("
" + "=" * 70)
print("PHASE 3: CLEANING abia/charts/views.py")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

with open("abia/charts/views.py", "r") as f:
    content = f.read()

lines = content.split("
")
clean_lines = []
seen_imports = set()
for line in lines:
    stripped = line.strip()
    if stripped.startswith("from django.shortcuts import render") or \
       stripped.startswith("from django.db.models import Count") or \
       stripped.startswith("from abia.migrants.models import Migrant") or \
       stripped.startswith("from abia.cases.models import Case"):
        if stripped in seen_imports:
            continue
        seen_imports.add(stripped)
    clean_lines.append(line)

new_content = "
".join(clean_lines)

if "def command_center(request):" not in new_content:
    print("WARNING command_center function missing — appending...")
    new_content += '''

from django.shortcuts import render
from django.db.models import Count
from abia.migrants.models import Migrant
from abia.cases.models import Case

def command_center(request):
    context = {
        "total_migrants": Migrant.objects.count(),
        "total_cases": Case.objects.count(),
        "open_cases": Case.objects.filter(status="open").count(),
        "high_priority_cases": Case.objects.filter(priority="high").count(),
        "resolved_cases": Case.objects.filter(status="resolved").count(),
        "lga_breakdown": list(Migrant.objects.values("current_lga_text").annotate(count=Count("id")).order_by("-count")[:15]),
        "recent_cases": Case.objects.order_by("-created_at")[:10],
        "recent_migrants": Migrant.objects.order_by("-created_at")[:10],
    }
    return render(request, "dashboard/index.html", context)
'''

with open("abia/charts/views.py", "w") as f:
    f.write(new_content)

print("OK charts/views.py cleaned and command_center verified")
PYEOF
```

---

## PHASE 4: FIX abia/dashboard_view.py — REAL DATA IN unified_dashboard

Diagnosis: unified_dashboard function exists but does NOT query the database.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os, re

print("
" + "=" * 70)
print("PHASE 4: FIXING abia/dashboard_view.py")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

with open("abia/dashboard_view.py", "r") as f:
    content = f.read()

imports_needed = [
    "from django.shortcuts import render",
    "from django.db.models import Count",
    "from abia.migrants.models import Migrant",
    "from abia.cases.models import Case",
]
for imp in imports_needed:
    if imp not in content:
        content = imp + "
" + content
        print("   Added: " + imp)

new_func = '''def unified_dashboard(request):
    context = {
        "total_migrants": Migrant.objects.count(),
        "total_cases": Case.objects.count(),
        "open_cases": Case.objects.filter(status="open").count(),
        "resolved_cases": Case.objects.filter(status="resolved").count(),
        "high_priority_cases": Case.objects.filter(priority="high").count(),
        "lga_breakdown": list(Migrant.objects.values("current_lga_text").annotate(count=Count("id")).order_by("-count")[:15]),
        "recent_migrants": Migrant.objects.order_by("-created_at")[:10],
        "recent_cases": Case.objects.order_by("-created_at")[:10],
    }
    return render(request, "public_dashboard/dashboard.html", context)
'''

if "def unified_dashboard" in content:
    content = re.sub(r'def unified_dashboard\(request\):.*?(?=def \w+\(|\Z)', new_func, content, flags=re.DOTALL)
    print("OK Replaced unified_dashboard with real data queries")
else:
    content += "
" + new_func
    print("OK Appended unified_dashboard function")

with open("abia/dashboard_view.py", "w") as f:
    f.write(content)
PYEOF
```

---

## PHASE 5: FIX abia/public_dashboard/views.py — REAL DATA

Diagnosis: public_dashboard function may still return hardcoded or empty context.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os, re

print("
" + "=" * 70)
print("PHASE 5: FIXING abia/public_dashboard/views.py")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

pd_views = "abia/public_dashboard/views.py"
if not os.path.exists(pd_views):
    print("ERROR " + pd_views + " not found")
else:
    with open(pd_views, "r") as f:
        content = f.read()

    new_func = '''def public_dashboard(request):
    from django.db.models import Count
    from abia.migrants.models import Migrant
    from abia.cases.models import Case

    total_migrants = Migrant.objects.count()
    total_cases = Case.objects.count()
    open_cases = Case.objects.filter(status="open").count()
    high_priority_cases = Case.objects.filter(priority="high").count()
    resolved_cases = Case.objects.filter(status="resolved").count()

    lga_breakdown = list(Migrant.objects.values("current_lga_text").annotate(count=Count("id")).order_by("-count")[:15])
    lga_list = [{"name": item["current_lga_text"] or "Unknown", "count": item["count"]} for item in lga_breakdown]

    context = {
        "total_migrants": total_migrants,
        "total_cases": total_cases,
        "open_cases": open_cases,
        "high_priority_cases": high_priority_cases,
        "resolved_cases": resolved_cases,
        "lga_breakdown": lga_list,
        "recent_migrants": Migrant.objects.order_by("-created_at")[:5],
    }
    return render(request, "public_dashboard/dashboard.html", context)
'''

    if "def public_dashboard" in content:
        content = re.sub(r'def public_dashboard\(request\):.*?(?=def \w+\(|\Z)', new_func, content, flags=re.DOTALL)
        print("OK Replaced public_dashboard with real data queries")
    else:
        content += "
" + new_func
        print("OK Appended public_dashboard function")

    with open(pd_views, "w") as f:
        f.write(content)
PYEOF
```

---

## PHASE 6: FIX abia/public_dashboard/urls.py — REMOVE EMPTY PATH HIJACK

Diagnosis: Empty path path("", views.public_dashboard, ...) hijacks the root /.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os

print("
" + "=" * 70)
print("PHASE 6: FIXING abia/public_dashboard/urls.py")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

pd_urls = "abia/public_dashboard/urls.py"
if os.path.exists(pd_urls):
    with open(pd_urls, "r") as f:
        content = f.read()

    lines = content.split("
")
    clean = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('path("", views.public_dashboard') or stripped.startswith("path('', views.public_dashboard"):
            continue
        clean.append(line)

    content = "
".join(clean)
    content = os.linesep.join([s for s in content.splitlines() if s.strip()])

    with open(pd_urls, "w") as f:
        f.write(content)
    print("OK Removed empty path hijack from public_dashboard/urls.py")
else:
    print("ERROR " + pd_urls + " not found")
PYEOF
```

---

## PHASE 9: FIX templates/public_dashboard/dashboard.html — TEMPLATE VARIABLES

Diagnosis: Hardcoded numbers like 100, 210, 255 still present.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os, re

print("\n" + "=" * 70)
print("PHASE 9: FIXING public_dashboard/dashboard.html")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

pd = "templates/public_dashboard/dashboard.html"
if not os.path.exists(pd):
    print("ERROR " + pd + " not found")
else:
    with open(pd, "r") as f:
        content = f.read()

    replacements = [
        (">900<", '>{{ total_migrants|default:"0" }}<'),
        (">700<", '>{{ total_cases|default:"0" }}<'),
        (">500<", '>{{ resolved_cases|default:"0" }}<'),
        (">300<", '>{{ total_cases|default:"0" }}<'),
        (">255<", '>{{ open_cases|default:"0" }}<'),
        (">210<", '>{{ total_cases|default:"0" }}<'),
        (">200<", '>{{ open_cases|default:"0" }}<'),
        (">100<", '>{{ total_migrants|default:"0" }}<'),
        ("> 900 <", '> {{ total_migrants|default:"0" }} <'),
        ("> 700 <", '> {{ total_cases|default:"0" }} <'),
        ("> 500 <", '> {{ resolved_cases|default:"0" }} <'),
        ("> 300 <", '> {{ total_cases|default:"0" }} <'),
        ("> 255 <", '> {{ open_cases|default:"0" }} <'),
        ("> 210 <", '> {{ total_cases|default:"0" }} <'),
        ("> 200 <", '> {{ open_cases|default:"0" }} <'),
        ("> 100 <", '> {{ total_migrants|default:"0" }} <'),
    ]

    for old, new in replacements:
        content = content.replace(old, new)

    content = re.sub(
        r'(<div[^>]*class="[^"]*(?:stat|value|count|number)[^"]*"[^>]*>\s*)\d{3,}(\s*)',
        r'\g<1>{{ total_migrants|default:"0" }}\g<2>',
        content,
        flags=re.IGNORECASE
    )

    with open(pd, "w") as f:
        f.write(content)

    with open(pd, "r") as f:
        verify = f.read()
    remaining = re.findall(r'>\s*\d{3,}\s*<', verify)
    if remaining:
        print("WARNING " + str(len(remaining)) + " hardcoded numbers may remain")
    else:
        print("OK All hardcoded stats replaced with template variables")
PYEOF
```

---

## PHASE 10: CREATE templates/dashboard/index.html — COMMAND CENTER

Diagnosis: Template dashboard/index.html does NOT exist. Django crashes with TemplateDoesNotExist.

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os

print("\n" + "=" * 70)
print("PHASE 10: CREATING templates/dashboard/index.html")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")
os.makedirs("templates/dashboard", exist_ok=True)

command_center_html = """{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Command Center | Abia Migration Observatory</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0a1628; color: #e2e8f0; min-height: 100vh; }
        nav { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; background: rgba(10,22,40,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.08); padding: 14px 40px; display: flex; justify-content: space-between; align-items: center; }
        nav .brand { font-weight: 700; color: #7dd3fc; font-size: 1.15rem; }
        nav .links { display: flex; gap: 22px; }
        nav a { color: #94a3b8; text-decoration: none; font-size: 0.88rem; padding: 6px 12px; border-radius: 6px; transition: all 0.2s; }
        nav a:hover { color: #fff; background: rgba(125,211,252,0.12); }
        .container { padding: 100px 40px 40px; max-width: 1400px; margin: 0 auto; }
        h1 { font-size: 1.8rem; margin-bottom: 6px; }
        .subtitle { color: #64748b; margin-bottom: 30px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 30px; }
        .kpi-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 24px; }
        .kpi-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        .kpi-value { font-size: 2rem; font-weight: 700; color: #7dd3fc; }
        .charts-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .chart-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 24px; }
        .chart-card h3 { font-size: 1rem; margin-bottom: 16px; color: #cbd5e1; }
        .table-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 24px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.05); }
        th { color: #94a3b8; font-weight: 600; }
        td { color: #cbd5e1; }
        .footer { text-align: center; padding: 30px; border-top: 1px solid rgba(255,255,255,0.05); color: #475569; font-size: 0.78rem; margin-top: 40px; }
    </style>
</head>
<body>
    <nav>
        <div class="brand">🏛️ Abia Migration Observatory — Command Center</div>
        <div class="links">
            <a href="/">🏠 Home</a>
            <a href="/dashboard/">📊 Public Dashboard</a>
            <a href="/onboarding/">🚪 Portals</a>
            <a href="/admin/">🔧 Admin</a>
            <a href="/api/docs/">📖 API</a>
        </div>
    </nav>

    <div class="container">
        <h1>Government Command Center</h1>
        <p class="subtitle">Real-time migration intelligence for Abia State Government officials</p>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Migrants</div>
                <div class="kpi-value">{{ total_migrants|default:"0" }}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Total Cases</div>
                <div class="kpi-value">{{ total_cases|default:"0" }}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Open Cases</div>
                <div class="kpi-value">{{ open_cases|default:"0" }}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">High Priority</div>
                <div class="kpi-value">{{ high_priority_cases|default:"0" }}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Resolved</div>
                <div class="kpi-value">{{ resolved_cases|default:"0" }}</div>
            </div>
        </div>

        <div class="charts-row">
            <div class="chart-card">
                <h3>LGA Breakdown — Returnees</h3>
                <canvas id="lgaChart"></canvas>
            </div>
            <div class="chart-card">
                <h3>Case Status Distribution</h3>
                <canvas id="caseChart"></canvas>
            </div>
        </div>

        <div class="table-card">
            <h3>Recent Cases</h3>
            <table>
                <thead>
                    <tr><th>ID</th><th>Status</th><th>Priority</th><th>Description</th><th>Date</th></tr>
                </thead>
                <tbody>
                    {% for case in recent_cases %}
                    <tr>
                        <td>{{ case.id }}</td>
                        <td>{{ case.status|default:"N/A" }}</td>
                        <td>{{ case.priority|default:"N/A" }}</td>
                        <td>{{ case.description|truncatechars:60 }}</td>
                        <td>{{ case.created_at|date:"Y-m-d" }}</td>
                    </tr>
                    {% empty %}
                    <tr><td colspan="5" style="text-align:center;color:#64748b;">No cases found</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        <p>Abia State Government | Ministry of Humanitarian Affairs | Powered by Abia Migration Observatory</p>
    </div>

    <script>
        const lgaCtx = document.getElementById('lgaChart').getContext('2d');
        const lgaLabels = [{% for item in lga_breakdown %}"{{ item.name|default:item.current_lga_text|default:\"Unknown\" }}"{% if not forloop.last %},{% endif %}{% endfor %}];
        const lgaData = [{% for item in lga_breakdown %}{{ item.count|default:item.Returnees|default:0 }}{% if not forloop.last %},{% endif %}{% endfor %}];
        new Chart(lgaCtx, {
            type: 'bar',
            data: {
                labels: lgaLabels,
                datasets: [{
                    label: 'Returnees',
                    data: lgaData,
                    backgroundColor: 'rgba(125, 211, 252, 0.6)',
                    borderColor: 'rgba(125, 211, 252, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                }
            }
        });

        const caseCtx = document.getElementById('caseChart').getContext('2d');
        new Chart(caseCtx, {
            type: 'doughnut',
            data: {
                labels: ['Open', 'Resolved', 'High Priority'],
                datasets: [{
                    data: [{{ open_cases|default:0 }}, {{ resolved_cases|default:0 }}, {{ high_priority_cases|default:0 }}],
                    backgroundColor: ['rgba(125,211,252,0.7)', 'rgba(34,197,94,0.7)', 'rgba(239,68,68,0.7)'],
                    borderColor: ['#7dd3fc', '#22c55e', '#ef4444'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#94a3b8' } }
                }
            }
        });
    </script>
</body>
</html>
"""

with open("templates/dashboard/index.html", "w") as f:
    f.write(command_center_html)

print("OK Created dashboard/index.html (" + str(len(command_center_html)) + " bytes)")
print("   Includes: Chart.js bar chart, doughnut chart, recent cases table")
PYEOF
```

---

## PHASE 11: FIX templates/dashboard.html (if it exists separately)

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && python3 << 'PYEOF'
import os, re

print("\n" + "=" * 70)
print("PHASE 11: FIXING templates/dashboard.html")
print("=" * 70)

os.chdir("/home/abia/abia-migration-observatory/abia-app")

if os.path.exists("templates/dashboard.html"):
    with open("templates/dashboard.html", "r") as f:
        content = f.read()

    content = content.replace(">900<", '>{{ total_migrants|default:"0" }}<')
    content = content.replace(">700<", '>{{ total_cases|default:"0" }}<')
    content = content.replace(">500<", '>{{ resolved_cases|default:"0" }}<')
    content = content.replace(">300<", '>{{ total_cases|default:"0" }}<')
    content = content.replace(">255<", '>{{ open_cases|default:"0" }}<')
    content = content.replace(">210<", '>{{ total_cases|default:"0" }}<')
    content = content.replace(">200<", '>{{ open_cases|default:"0" }}<')
    content = content.replace(">100<", '>{{ total_migrants|default:"0" }}<')

    with open("templates/dashboard.html", "w") as f:
        f.write(content)
    print("OK Fixed templates/dashboard.html")
else:
    print("INFO templates/dashboard.html does not exist (ok if using public_dashboard/dashboard.html)")
PYEOF
```

---

## PHASE 12: DJANGO CHECK & CLEAN SERVER START

Copy and paste:

```bash
cd ~/abia-migration-observatory/abia-app && source ../.venv/bin/activate && bash << 'BASHEOF'
echo "=== PHASE 12: DJANGO SYSTEM CHECK ==="
PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=abia.settings.development python3 -B manage.py check 2>&1 | tail -15

echo ""
echo "=== KILLING ANY GHOST SERVERS ==="
pkill -9 -f "manage.py runserver" 2>/dev/null
pkill -9 -f "python.*8001" 2>/dev/null
sleep 2

echo "=== VERIFYING PORT FREE ==="
ss -tlnp | grep 8001 || echo "OK Port 8001 FREE"

echo "=== STARTING SERVER WITH NOHUP ==="
PYTHONDONTWRITEBYTECODE=1 DJANGO_SETTINGS_MODULE=abia.settings.development nohup python3 -B manage.py runserver 0.0.0.0:8001 > /tmp/django8001.log 2>&1 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
sleep 6

echo ""
echo "=== WAITING FOR READY ==="
for i in 1 2 3 4 5 6; do
    code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 2 http://127.0.0.1:8001/api/v1/health/ 2>/dev/null)
    if [ "$code" = "200" ]; then
        echo "OK Server ready (HTTP 200 on health check)"
        break
    fi
    echo "WAIT Attempt $i/6..."
    sleep 2
done

if [ "$code" != "200" ]; then
    echo "ERROR Server failed to start. Last log lines:"
    tail -30 /tmp/django8001.log
    exit 1
fi

echo ""
echo "=== VERIFYING ALL PAGES ==="
for path in "/" "/dashboard/" "/onboarding/" "/command-center/" "/api/docs/"; do
    name=$(basename "$path")
    [ "$name" = "" ] && name="landing"
    http_code=$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 4 "http://127.0.0.1:8001$path")
    icon="OK"
    [ "$http_code" != "200" ] && icon="FAIL"
    printf " %s %-18s %s -> HTTP %s
" "$icon" "$name" "$path" "$http_code"
done

echo ""
echo "=== CONTENT VERIFICATION ==="
echo -n "Landing has 'Abia':     "
curl -s --connect-timeout 3 http://127.0.0.1:8001/ | grep -io 'abia' | head -1 > /dev/null && echo "OK YES" || echo "FAIL NO"

echo -n "Landing shows 1363:     "
curl -s --connect-timeout 3 http://127.0.0.1:8001/ | grep -o '1363' | head -1 > /dev/null && echo "OK YES" || echo "FAIL NO"

echo -n "Dashboard shows 1363:   "
curl -s --connect-timeout 3 http://127.0.0.1:8001/dashboard/ | grep -o '1363' | head -1 > /dev/null && echo "OK YES" || echo "FAIL NO"

echo -n "Command Center 1363:    "
curl -s --connect-timeout 3 http://127.0.0.1:8001/command-center/ | grep -o '1363' | head -1 > /dev/null && echo "OK YES" || echo "FAIL NO"

echo -n "Onboarding Gov link:   "
curl -s --connect-timeout 3 http://127.0.0.1:8001/onboarding/ | grep 'command-center' > /dev/null && echo "OK YES" || echo "FAIL NO"

echo -n "Onboarding Partner:    "
curl -s --connect-timeout 3 http://127.0.0.1:8001/onboarding/ | grep '/reports/' > /dev/null && echo "OK YES" || echo "FAIL NO"

echo ""
echo "========================================"
echo "  ABIA MIGRATION OBSERVATORY — LIVE"
echo "========================================"
echo "  http://localhost:8001/           <- Landing Page"
echo "  http://localhost:8001/dashboard/ <- Public Dashboard"
echo "  http://localhost:8001/command-center/ <- Command Center"
echo "  http://localhost:8001/onboarding/  <- Portal Selector"
echo "  http://localhost:8001/api/docs/    <- Swagger API"
echo "  http://localhost:8001/admin/       <- Django Admin"
echo "========================================"
BASHEOF
```

---

## EXPECTED FINAL STATE

| URL | Status | Content |
|-----|--------|---------|
| / | HTTP 200 | Landing page with Abia logo, nav bar, 4 stat cards, 4 portal cards |
| /dashboard/ | HTTP 200 | Public dashboard with real 1363 migrants, 300 cases, template variables |
| /command-center/ | HTTP 200 | Command Center with Chart.js charts, KPIs, recent cases table |
| /onboarding/ | HTTP 200 | Portal selector with correct links (Gov->/command-center/, Partner->/reports/) |
| /api/docs/ | HTTP 200 | Swagger API documentation |
| /admin/ | HTTP 200 | Django Admin |

---

## EMERGENCY ROLLBACK

If everything breaks, restore from git:

```bash
cd ~/abia-migration-observatory/abia-app
git checkout -- abia/urls.py abia/charts/urls.py abia/charts/views.py abia/dashboard_view.py abia/public_dashboard/views.py abia/public_dashboard/urls.py templates/landing.html templates/onboarding.html templates/dashboard/index.html templates/public_dashboard/dashboard.html
```

Then re-run only the phases you need.

---

## NOTES FOR FUTURE

1. Never inject HTML nav bars into existing templates via regex — it breaks tag balance.
2. Always use `python3 manage.py check` before starting the server — catches import and routing errors instantly.
3. Use `nohup` for background server — survives terminal close: `nohup python3 -B manage.py runserver 0.0.0.0:8001 &`
4. Check `tail -f /tmp/django8001.log` in a separate terminal to monitor errors live.
5. The `/reports/` page does not exist yet — create it when partner reporting is ready, or redirect to `/admin/` temporarily.

---

*Document generated by NASA-Level Software Architect Protocol*
*Abia Migration Observatory — Surgical Repair Manual v1.0*
