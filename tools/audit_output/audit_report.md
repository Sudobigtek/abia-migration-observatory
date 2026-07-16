# Codebase Audit Report


# Codebase Audit Summary
Total files scanned: 3822
Issues found: 29
    Errors: 5
    Warnings: 24
    Info: 0

Tests: 0 passed, 0 failed, 0 errors.

Auto-fix script generated (use --fix to execute).


## Detailed Issues

- **/home/abia/abia-migration-observatory/settings_secrets_patch.py**:7 [error] syntax: invalid syntax (<unknown>, line 7)
- **/home/abia/abia-migration-observatory/abia-app/fix_created_by.py**:30 [error] syntax: unterminated string literal (detected at line 30) (<unknown>, line 30)
- **/home/abia/abia-migration-observatory/abia/migrants/odk_webhook_view.py**:8 [error] syntax: invalid syntax (<unknown>, line 8)
- **/home/abia/abia-migration-observatory/abia-app/dynamic_fields/settings_secrets_patch.py**:7 [error] syntax: invalid syntax (<unknown>, line 7)
- **/home/abia/abia-migration-observatory/abia-app/dynamic_fields/diagnose_repos.py**:13 [error] syntax: unterminated string literal (detected at line 13) (<unknown>, line 13)
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/rest_framework/renderers.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/forms/fields.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/contrib/admin/utils.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/contrib/postgres/fields/jsonb.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/contrib/postgres/fields/hstore.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/contrib/postgres/aggregates/general.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/contrib/postgres/forms/hstore.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/core/serializers/xml_serializer.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/models/__init__.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/models/fields/json.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/models/functions/json.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/mysql/introspection.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/mysql/base.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/mysql/operations.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/oracle/introspection.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/oracle/base.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/oracle/operations.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/postgresql/introspection.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/postgresql/base.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/postgresql/psycopg_any.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/sqlite3/introspection.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/django/db/backends/sqlite3/base.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/rest_framework/utils/field_mapping.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.
- **/home/abia/abia-migration-observatory/.venv/lib/python3.14/site-packages/rest_framework/schemas/openapi.py**:0 [warning] dynamic_fields: JSONField or HStoreField without default/blank might cause database errors.


## Auto-fix Script

```bash
#!/bin/bash
# Auto-generated fix script by Codebase Doctor

echo 'Running isort...'
isort . --profile black 2>/dev/null || true
echo 'Running black...'
black . 2>/dev/null || true
echo 'Running autopep8...'
autopep8 --in-place --recursive . 2>/dev/null || true
echo 'Running Django migrations if needed...'
python manage.py makemigrations 2>/dev/null || true
python manage.py migrate 2>/dev/null || true
echo 'Running tests to verify fixes...'
pytest 2>/dev/null || true
echo 'Fix script completed.'
```
