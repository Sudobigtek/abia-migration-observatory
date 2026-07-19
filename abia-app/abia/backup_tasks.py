from celery import shared_task
from .backup import create_backup, cleanup_old_backups

@shared_task
def daily_backup():
    result = create_backup()
    if result['success']:
        cleanup_old_backups(keep_days=30)
    return result

@shared_task
def weekly_cleanup():
    return cleanup_old_backups(keep_days=14)
