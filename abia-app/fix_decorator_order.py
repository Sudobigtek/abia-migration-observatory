import os

files = [
    "abia/common/views.py", "abia/analytics/views.py", "abia/audit/views.py",
    "abia/backup/views.py", "abia/cbn/views.py", "abia/charts/views.py",
    "abia/common/gateway.py", "abia/webhooks/views.py",
    "abia/worldbank/views.py", "abia/wto/views.py"
]

for path in files:
    if not os.path.exists(path):
        continue
    with open(path) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if "@extend_schema(" in lines[i]:
            start = i
            while i < len(lines) and not lines[i].strip().endswith(")"):
                i += 1
            if i < len(lines):
                i += 1
            block = lines[start:i]
            del lines[start:i]
            j = start - 1
            while j >= 0 and lines[j].strip().startswith("@"):
                j -= 1
            insert = j + 1
            lines[insert:insert] = block
            i = insert + len(block)
        else:
            i += 1
    with open(path, "w") as f:
        f.writelines(lines)
    print("Fixed", path)
