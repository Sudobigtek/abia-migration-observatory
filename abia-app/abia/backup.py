import os
import subprocess
import datetime

def get_db_config():
    """Extract database config from environment."""
    return {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', ''),
        'name': os.environ.get('POSTGRES_DB', 'abia_migration_db'),
    }

def create_backup(backup_dir="/backups"):
    """Create a PostgreSQL dump backup."""
    os.makedirs(backup_dir, exist_ok=True)
    cfg = get_db_config()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"abia_backup_{timestamp}.sql"
    filepath = os.path.join(backup_dir, filename)

    env = os.environ.copy()
    env['PGPASSWORD'] = cfg['password']

    cmd = [
        'pg_dump', '-h', cfg['host'], '-p', cfg['port'],
        '-U', cfg['user'], '-d', cfg['name'],
        '-F', 'c', '-f', filepath,
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode == 0:
        schema_file = os.path.join(backup_dir, f"abia_schema_{timestamp}.sql")
        schema_cmd = [
            'pg_dump', '-h', cfg['host'], '-p', cfg['port'],
            '-U', cfg['user'], '-d', cfg['name'],
            '--schema-only', '-f', schema_file
        ]
        subprocess.run(schema_cmd, env=env, capture_output=True)
        return {
            'success': True,
            'file': filepath,
            'schema': schema_file,
            'size': os.path.getsize(filepath)
        }
    return {'success': False, 'error': result.stderr}

def restore_backup(backup_file, host=None, port=None, user=None, password=None, dbname=None):
    """Restore from a PostgreSQL backup file."""
    cfg = get_db_config()
    env = os.environ.copy()
    env['PGPASSWORD'] = password or cfg['password']
    cmd = [
        'pg_restore', '-h', host or cfg['host'], '-p', str(port or cfg['port']),
        '-U', user or cfg['user'], '-d', dbname or cfg['name'],
        '--clean', '--if-exists', backup_file
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return {'success': result.returncode == 0, 'error': result.stderr if result.returncode != 0 else None}

def list_backups(backup_dir="/backups"):
    """List all available backups."""
    if not os.path.exists(backup_dir):
        return []
    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.startswith('abia_backup_') and f.endswith('.sql'):
            filepath = os.path.join(backup_dir, f)
            backups.append({
                'filename': f,
                'created': datetime.datetime.fromtimestamp(os.path.getctime(filepath)).isoformat(),
                'size_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                'path': filepath,
            })
    return backups

def cleanup_old_backups(backup_dir="/backups", keep_days=30):
    """Remove backups older than keep_days."""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=keep_days)
    removed = 0
    for backup in list_backups(backup_dir):
        created = datetime.datetime.fromisoformat(backup['created'])
        if created < cutoff:
            os.remove(backup['path'])
            schema_file = backup['path'].replace('abia_backup_', 'abia_schema_')
            if os.path.exists(schema_file):
                os.remove(schema_file)
            removed += 1
    return {'removed': removed, 'kept': len(list_backups(backup_dir))}
