from django.test import TestCase
from django.core.management import call_command


class SchemaValidationTests(TestCase):
    def test_schema_generates_without_errors(self):
        """Fail the test if drf-spectacular produces errors."""
        call_command('spectacular', '--file', '/tmp/test_schema.yml', '--validate')
