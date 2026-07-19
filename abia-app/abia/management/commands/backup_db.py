from django.core.management.base import BaseCommand
from abia.backup import create_backup, list_backups, cleanup_old_backups

class Command(BaseCommand):
    help = "Create, list, or manage database backups"

    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, default='create', choices=['create', 'list', 'cleanup'])
        parser.add_argument('--dir', type=str, default='/backups')
        parser.add_argument('--keep-days', type=int, default=30)

    def handle(self, *args, **options):
        action = options['action']
        backup_dir = options['dir']
        if action == 'create':
            result = create_backup(backup_dir)
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f"Backup: {result['file']} ({result['size']} bytes)"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed: {result['error']}"))
        elif action == 'list':
            for b in list_backups(backup_dir):
                self.stdout.write(f"  {b['filename']} - {b['size_mb']} MB - {b['created']}")
        elif action == 'cleanup':
            result = cleanup_old_backups(backup_dir, options['keep_days'])
            self.stdout.write(self.style.SUCCESS(f"Removed {result['removed']}, {result['kept']} remaining"))
