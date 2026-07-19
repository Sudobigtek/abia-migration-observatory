from django.core.management.base import BaseCommand
from abia.backup import restore_backup

class Command(BaseCommand):
    help = "Restore database from a backup file"
    def add_arguments(self, parser):
        parser.add_argument('backup_file', type=str)
        parser.add_argument('--host', type=str, default='localhost')
        parser.add_argument('--port', type=str, default='5432')
        parser.add_argument('--user', type=str, default='postgres')
        parser.add_argument('--dbname', type=str, default='abia_migration_db')
    def handle(self, *args, **options):
        result = restore_backup(options['backup_file'], host=options['host'], port=options['port'], user=options['user'], dbname=options['dbname'])
        if result['success']:
            self.stdout.write(self.style.SUCCESS("Restored successfully"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed: {result['error']}"))
