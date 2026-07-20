import hashlib
import os
import subprocess
from datetime import datetime
from django.conf import settings
from .models import BackupJob, RestoreJob

class BackupService:
    BACKUP_DIR = os.path.join(settings.BASE_DIR, "..", "backups")

    @staticmethod
    def ensure_backup_dir():
        os.makedirs(BackupService.BACKUP_DIR, exist_ok=True)

    @staticmethod
    def calculate_checksum(file_path):
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def run_pg_dump(job):
        BackupService.ensure_backup_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"abia_backup_{job.backup_type}_{timestamp}.sql"
        file_path = os.path.join(BackupService.BACKUP_DIR, filename)
        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["PGPASSWORD"] = db.get("PASSWORD", "")
        cmd = [
            "pg_dump",
            "-h", db.get("HOST", "localhost"),
            "-p", str(db.get("PORT", 5432)),
            "-U", db.get("USER", "postgres"),
            "-d", db.get("NAME", "abia_migration"),
            "-f", file_path,
        ]
        if job.backup_type == "schema":
            cmd.append("--schema-only")
        elif job.backup_type == "data":
            cmd.append("--data-only")
        job.status = "running"
        job.started_at = datetime.now()
        job.save()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=3600)
            if result.returncode == 0:
                job.status = "completed"
                job.file_path = file_path
                job.file_size = os.path.getsize(file_path)
                job.checksum = BackupService.calculate_checksum(file_path)
            else:
                job.status = "failed"
                job.error_message = result.stderr[:500]
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)[:500]
        job.completed_at = datetime.now()
        job.save()
        return job

    @staticmethod
    def run_restore(restore_job):
        backup = restore_job.backup
        if not os.path.exists(backup.file_path):
            restore_job.status = "failed"
            restore_job.error_message = "Backup file not found"
            restore_job.save()
            return restore_job
        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["PGPASSWORD"] = db.get("PASSWORD", "")
        cmd = [
            "psql",
            "-h", db.get("HOST", "localhost"),
            "-p", str(db.get("PORT", 5432)),
            "-U", db.get("USER", "postgres"),
            "-d", db.get("NAME", "abia_migration"),
            "-f", backup.file_path,
        ]
        restore_job.status = "running"
        restore_job.started_at = datetime.now()
        restore_job.save()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=7200)
            if result.returncode == 0:
                restore_job.status = "completed"
            else:
                restore_job.status = "failed"
                restore_job.error_message = result.stderr[:500]
        except Exception as e:
            restore_job.status = "failed"
            restore_job.error_message = str(e)[:500]
        restore_job.completed_at = datetime.now()
        restore_job.save()
        return restore_job

    @staticmethod
    def list_backups():
        BackupService.ensure_backup_dir()
        files = []
        for f in os.listdir(BackupService.BACKUP_DIR):
            if f.endswith(".sql"):
                fp = os.path.join(BackupService.BACKUP_DIR, f)
                files.append({
                    "name": f,
                    "size": os.path.getsize(fp),
                    "modified": datetime.fromtimestamp(os.path.getmtime(fp)).isoformat(),
                })
        return sorted(files, key=lambda x: x["modified"], reverse=True)