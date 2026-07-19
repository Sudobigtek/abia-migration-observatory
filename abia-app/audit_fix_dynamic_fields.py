#!/usr/bin/env python3
"""
DYNAMIC FIELDS AUDIT & SURGICAL FIX
Abia Migration Observatory
Run from: ~/abia-migration-observatory/abia-app/
"""

import os
import shutil
import sys

DF_DIR = "dynamic_fields"
BACKUP_DIR = f"dynamic_fields_backup_{os.getpid()}"


def backup_files():
    print("\n[1/5] Backing up existing files...")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for f in ["models.py", "admin.py", "services.py", "tests.py"]:
        src = os.path.join(DF_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, BACKUP_DIR)
            print(f"  Backed up {f}")


def fix_models():
    print("\n[2/5] Fixing models.py...")
    content = open(f"{BACKUP_DIR}/models.py").read()

    # Fix 1: Add blank=True to created_by FKs so admin form validates
    content = content.replace(
        "created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,",
        "created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,",
    )
    content = content.replace(
        "updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,",
        "updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,",
    )

    # Fix 2: Add save() method to auto-set created_by from request
    old_meta = """    class Meta:
        ordering = ['entity_type', 'order', 'field_name']"""
    new_meta = """    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by_id:
            from django.http import HttpRequest
            from threading import local
            _thread_locals = local()
            if hasattr(_thread_locals, 'request') and hasattr(_thread_locals.request, 'user'):
                if _thread_locals.request.user.is_authenticated:
                    self.created_by = _thread_locals.request.user
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['entity_type', 'order', 'field_name']"""
    content = content.replace(old_meta, new_meta)

    # Fix 3: Safe __str__ for EntityDynamicData
    content = content.replace(
        "return f'{self.entity_type}:{self.entity_id} ({len(self.data)} fields)'",
        "field_count = len(self.data) if isinstance(self.data, dict) else 0\n        return f'{self.entity_type}:{self.entity_id} ({field_count} fields)'",
    )

    with open(f"{DF_DIR}/models.py", "w") as f:
        f.write(content)
    print("  Fixed: blank=True on FKs, auto created_by, safe __str__")


def fix_admin():
    print("\n[3/5] Fixing admin.py...")
    content = open(f"{BACKUP_DIR}/admin.py").read()

    # Fix: Ensure save_model sets created_by
    old_save = """    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)"""
    new_save = """    def save_model(self, request, obj, form, change):
        if not change or not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)"""
    content = content.replace(old_save, new_save)

    # Add created_by_display if missing
    if "created_by_display" not in content:
        old_class = "class DynamicFieldDefinitionAdmin(admin.ModelAdmin):"
        new_class = """class DynamicFieldDefinitionAdmin(admin.ModelAdmin):
    def created_by_display(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return 'SYSTEM'
    created_by_display.short_description = 'Created By'"""
        content = content.replace(old_class, new_class)

        # Add to list_display
        content = content.replace(
            "'field_name', 'label', 'entity_type', 'field_type',",
            "'field_name', 'label', 'entity_type', 'field_type', 'created_by_display',",
        )

    with open(f"{DF_DIR}/admin.py", "w") as f:
        f.write(content)
    print("  Fixed: save_model sets created_by, audit display")


def fix_services():
    print("\n[4/5] Fixing services.py...")
    content = open(f"{BACKUP_DIR}/services.py").read()

    # Fix: _validate_integer must check min/max bounds
    old_int = """    @staticmethod
    def _validate_integer(defn, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError('Expected integer')"""
    new_int = """    @staticmethod
    def _validate_integer(defn, value):
        try:
            num = int(value)
        except (TypeError, ValueError):
            raise ValidationError('Expected integer')
        if defn.min_value is not None and num < defn.min_value:
            raise ValidationError(f'Minimum value: {defn.min_value}')
        if defn.max_value is not None and num > defn.max_value:
            raise ValidationError(f'Maximum value: {defn.max_value}')
        return num"""
    content = content.replace(old_int, new_int)

    # Fix: set_field_value must set created_by on new records
    old_set = """            obj, created = DynamicFieldValue.objects.update_or_create(
                definition=definition,
                entity_type=entity_type,
                entity_id=entity_id,
                defaults={
                    'value': validated if not definition.is_sensitive else None,
                    'updated_by': user,
                }
            )"""
    new_set = """            obj, created = DynamicFieldValue.objects.update_or_create(
                definition=definition,
                entity_type=entity_type,
                entity_id=entity_id,
                defaults={
                    'value': validated if not definition.is_sensitive else None,
                    'updated_by': user,
                }
            )
            if created:
                obj.created_by = user
                obj.save(update_fields=['created_by'])"""
    content = content.replace(old_set, new_set)

    with open(f"{DF_DIR}/services.py", "w") as f:
        f.write(content)
    print("  Fixed: integer bounds, created_by on values")


def fix_tests():
    print("\n[5/5] Fixing tests.py...")
    content = open(f"{BACKUP_DIR}/tests.py").read()

    # Fix: Add test for created_by on values
    if "test_created_by_set_on_value" not in content:
        old_test = "class ODKFormGenerationTests(TestCase):"
        new_test = """    def test_created_by_set_on_value(self):
        obj = DynamicFieldService.set_field_value(self.defn, EntityType.MIGRANT, 3, 'economic', self.user)
        self.assertEqual(obj.created_by, self.user)
        self.assertEqual(obj.updated_by, self.user)

class ODKFormGenerationTests(TestCase):"""
        content = content.replace(old_test, new_test)

    with open(f"{DF_DIR}/tests.py", "w") as f:
        f.write(content)
    print("  Fixed: added created_by audit test")


def main():
    print("=" * 60)
    print("  DYNAMIC FIELDS AUDIT & SURGICAL FIX")
    print("=" * 60)

    if not os.path.exists(DF_DIR):
        print(f"ERROR: {DF_DIR}/ directory not found. Run from abia-app/")
        sys.exit(1)

    backup_files()
    fix_models()
    fix_admin()
    fix_services()
    fix_tests()

    print("\n" + "=" * 60)
    print("  FIX COMPLETE")
    print("=" * 60)
    print(f"\nBackup saved to: {BACKUP_DIR}/")
    print("\nNext steps:")
    print("  python manage.py makemigrations dynamic_fields")
    print("  python manage.py migrate")
    print("  python manage.py test dynamic_fields")
    print("  python manage.py runserver 0.0.0.0:8002")
    print("\nThen login to admin and create a field.")
    print("created_by will show your username automatically.")


if __name__ == "__main__":
    main()
