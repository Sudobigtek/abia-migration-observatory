#!/usr/bin/env python3
"""ABIA Test Environment Bootstrap — PEP 668 Compliant Auto-Setup.

Recreate 2026-07-12: Now handles Ubuntu 24.04+ externally-managed environments
by auto-creating a virtual environment and installing dependencies into it.

Usage:
    # Copy from Windows Downloads to WSL:
    cp /mnt/c/Users/Admin/Downloads/fix_tests_contract_compliant.py \
       ~/abia-migration-observatory/

    cd ~/abia-migration-observatory
    python3 fix_tests_contract_compliant.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

# ──────────────────────────────────────────────────────────────────────────────
# Custom Domain Exceptions (Contract §1.3, §4.2)
# ──────────────────────────────────────────────────────────────────────────────


class ABIAEnvironmentError(Exception):
    """Base exception for ABIA environment setup failures."""

    pass


class ContainerNotRunningError(ABIAEnvironmentError):
    """Raised when a required Docker container is not running."""

    pass


class DependencyInstallError(ABIAEnvironmentError):
    """Raised when Python package installation fails."""

    pass


class PathNotFoundError(ABIAEnvironmentError):
    """Raised when an expected filesystem path does not exist."""

    pass


# ──────────────────────────────────────────────────────────────────────────────
# Enums & Constants (Contract §5.1)
# ──────────────────────────────────────────────────────────────────────────────


class EnvironmentType(Enum):
    """Runtime environment classification."""

    DOCKER = "docker"
    WSL = "wsl"
    HOST = "host"


DEFAULT_POSTGRES_PORT: Final[str] = "5432"
DEFAULT_POSTGRES_DB: Final[str] = "abia_app_test"
DEFAULT_POSTGRES_USER: Final[str] = "postgres"
DEFAULT_POSTGRES_PASSWORD: Final[str] = "changeme"
VENV_DIR: Final[str] = ".venv"
REQUIRED_PACKAGES: Final[list[str]] = ["pytest", "pytest-django"]


# ──────────────────────────────────────────────────────────────────────────────
# Data Transfer Objects
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ContainerStatus:
    """Status of required Docker containers."""

    postgres_running: bool
    redis_running: bool


# ──────────────────────────────────────────────────────────────────────────────
# Service Layer (Contract §4.1 — Business Logic, no ORM imports)
# ──────────────────────────────────────────────────────────────────────────────


class EnvironmentService:
    """Orchestrates environment detection and validation."""

    @staticmethod
    def detect_environment() -> EnvironmentType:
        """Detect whether running in Docker, WSL, or bare host."""
        if Path("/.dockerenv").exists():
            return EnvironmentType.DOCKER
        proc_version = Path("/proc/version")
        if proc_version.exists() and "microsoft" in proc_version.read_text().lower():
            return EnvironmentType.WSL
        return EnvironmentType.HOST

    @staticmethod
    def resolve_database_host(env_type: EnvironmentType) -> str:
        """Resolve PostgreSQL host based on environment."""
        if env_type == EnvironmentType.DOCKER:
            return "postgres"
        return "localhost"

    @staticmethod
    def validate_project_structure(project_root: Path) -> None:
        """Ensure required directories exist or can be created."""
        app_dir = project_root / "abia-app"
        abia_dir = app_dir / "abia"

        if not app_dir.exists():
            raise PathNotFoundError(
                f"Application directory not found: {app_dir}. "
                f"Ensure you are in the project root."
            )

        abia_dir.mkdir(parents=True, exist_ok=True)


class VirtualEnvironmentService:
    """Manages Python virtual environment lifecycle per PEP 668."""

    @staticmethod
    def is_venv_active() -> bool:
        """Check if currently running inside a virtual environment."""
        return hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

    @staticmethod
    def venv_exists(project_root: Path) -> bool:
        """Check if .venv directory exists."""
        return (project_root / VENV_DIR / "bin" / "python").exists()

    @staticmethod
    def create_venv(project_root: Path) -> Path:
        """Create a new virtual environment."""
        venv_path = project_root / VENV_DIR
        print(f"    Creating virtual environment at {venv_path}...")
        venv.create(venv_path, with_pip=True)
        return venv_path / "bin" / "python"

    @staticmethod
    def install_packages(python_path: Path, packages: list[str]) -> None:
        """Install packages into the virtual environment."""
        print(f"    Installing: {', '.join(packages)}...")
        result = subprocess.run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
            capture_output=True,
            text=True,
            check=False,
        )
        result = subprocess.run(
            [str(python_path), "-m", "pip", "install"] + packages,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise DependencyInstallError(f"Failed to install packages: {result.stderr}")
        print("    ✓ Dependencies installed")

    @staticmethod
    def ensure_venv_and_deps(project_root: Path) -> Path:
        """Ensure venv exists and has required packages. Returns python path."""
        python_path = project_root / VENV_DIR / "bin" / "python"

        if not VirtualEnvironmentService.venv_exists(project_root):
            python_path = VirtualEnvironmentService.create_venv(project_root)

        if not VirtualEnvironmentService.is_venv_active():
            print("\n⚠️  PEP 668: System Python is externally managed.")
            print("    Using project virtual environment instead.\n")

        VirtualEnvironmentService.install_packages(python_path, REQUIRED_PACKAGES)
        return python_path


# ──────────────────────────────────────────────────────────────────────────────
# Repository Layer (Contract §4.1 — Data Access only)
# ──────────────────────────────────────────────────────────────────────────────


class ContainerRepository:
    """Abstracts Docker container state queries."""

    @staticmethod
    def list_running_containers() -> list[str]:
        """Return list of currently running container names."""
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return []
        return [name.strip() for name in result.stdout.split("\n") if name.strip()]

    @staticmethod
    def is_container_running(name: str) -> bool:
        """Check if a specific container is running."""
        return name in ContainerRepository.list_running_containers()


class DatabaseRepository:
    """Abstracts PostgreSQL operations."""

    @staticmethod
    def create_test_database(
        container_name: str,
        db_name: str,
        user: str = DEFAULT_POSTGRES_USER,
    ) -> bool:
        """Create test database via docker exec."""
        cmd = [
            "docker",
            "exec",
            container_name,
            "psql",
            "-U",
            user,
            "-c",
            f"CREATE DATABASE {db_name};",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0 or "already exists" in result.stderr


class FileRepository:
    """Abstracts filesystem write operations."""

    @staticmethod
    def write_text(path: Path, content: str) -> None:
        """Atomically write text content to a file."""
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def make_executable(path: Path) -> None:
        """Set executable permission on a file."""
        path.chmod(path.stat().st_mode | 0o111)


# ──────────────────────────────────────────────────────────────────────────────
# Controller / CLI (Contract §4.1 — Thin controller, max 30 lines)
# ──────────────────────────────────────────────────────────────────────────────


class TestEnvironmentCLI:
    """Command-line interface for test environment setup."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.app_dir = project_root / "abia-app"
        self.abia_dir = self.app_dir / "abia"

    def run(self) -> int:
        """Execute the full setup workflow. Returns exit code."""
        try:
            self._print_header()
            self._ensure_dependencies()
            env_type = self._detect_environment()
            self._validate_structure()
            self._check_containers()
            self._generate_configs(env_type)
            self._ensure_database(env_type)
            self._generate_run_script()
            self._print_success()
            return 0
        except ABIAEnvironmentError as exc:
            print(f"\n❌ Setup failed: {exc}", file=sys.stderr)
            return 1

    def _print_header(self) -> None:
        """Display setup banner."""
        print("=" * 50)
        print("ABIA TEST ENVIRONMENT SETUP")
        print("=" * 50)

    def _ensure_dependencies(self) -> None:
        """Ensure Python dependencies are available (PEP 668 safe)."""
        print("\n[0] Checking Python dependencies...")
        try:
            import pytest  # noqa: F401

            print("    ✓ pytest already available")
        except ImportError:
            VirtualEnvironmentService.ensure_venv_and_deps(self.project_root)

    def _detect_environment(self) -> EnvironmentType:
        """Detect and report runtime environment."""
        env_type = EnvironmentService.detect_environment()
        print(f"\n[1] Environment: {env_type.value.upper()}")
        return env_type

    def _validate_structure(self) -> None:
        """Validate project directory structure."""
        EnvironmentService.validate_project_structure(self.project_root)
        print("[2] Project structure validated")

    def _check_containers(self) -> ContainerStatus:
        """Check required Docker containers."""
        pg_running = ContainerRepository.is_container_running("abia-postgres")
        redis_running = ContainerRepository.is_container_running("abia-redis")
        print(f"[3] PostgreSQL: {'RUNNING ✓' if pg_running else 'NOT RUNNING ✗'}")
        print(f"[4] Redis: {'RUNNING ✓' if redis_running else 'NOT RUNNING ✗'}")
        if not pg_running:
            raise ContainerNotRunningError(
                "PostgreSQL container 'abia-postgres' is not running. "
                "Start it with: docker compose up -d abia-postgres"
            )
        return ContainerStatus(postgres_running=pg_running, redis_running=redis_running)

    def _generate_configs(self, env_type: EnvironmentType) -> None:
        """Generate test_settings.py and pytest.ini."""
        host = EnvironmentService.resolve_database_host(env_type)
        print(f"[5] Database host: {host}")
        self._write_test_settings(host)
        self._write_pytest_ini()

    def _write_test_settings(self, host: str) -> None:
        """Generate abia/test_settings.py."""
        content = f"""from .settings import *

DATABASES = {{
    'default': {{
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('POSTGRES_DB', '{DEFAULT_POSTGRES_DB}'),
        'USER': os.getenv('POSTGRES_USER', '{DEFAULT_POSTGRES_USER}'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', '{DEFAULT_POSTGRES_PASSWORD}'),
        'HOST': os.getenv('POSTGRES_HOST', '{host}'),
        'PORT': os.getenv('POSTGRES_PORT', '{DEFAULT_POSTGRES_PORT}'),
    }}
}}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
CELERY_TASK_ALWAYS_EAGER = True
CACHES = {{
    'default': {{
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }}
}}
"""
        path = self.abia_dir / "test_settings.py"
        FileRepository.write_text(path, content)
        print(f"[6] Created: {path}")

    def _write_pytest_ini(self) -> None:
        """Generate pytest.ini."""
        content = """[pytest]
DJANGO_SETTINGS_MODULE = abia.test_settings
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short --reuse-db
"""
        path = self.app_dir / "pytest.ini"
        FileRepository.write_text(path, content)
        print(f"[7] Created: {path}")

    def _ensure_database(self, env_type: EnvironmentType) -> None:
        """Create test database if running outside Docker."""
        if env_type != EnvironmentType.DOCKER:
            print("[8] Creating test database...")
            success = DatabaseRepository.create_test_database(
                "abia-postgres", DEFAULT_POSTGRES_DB
            )
            status = "✓ Ready" if success else "⚠ May already exist"
            print(f"     {status}")

    def _generate_run_script(self) -> None:
        """Generate run_tests.sh wrapper."""
        content = """#!/bin/bash
cd "$(dirname "$0")/abia-app"
pytest "$@"
"""
        path = self.project_root / "run_tests.sh"
        FileRepository.write_text(path, content)
        FileRepository.make_executable(path)
        print(f"[9] Created: {path}")

    def _print_success(self) -> None:
        """Display completion message."""
        print("\n" + "=" * 50)
        print("SETUP COMPLETE!")
        print("=" * 50)
        print("Next steps:")
        venv_hint = (
            "source .venv/bin/activate && "
            if not VirtualEnvironmentService.is_venv_active()
            else ""
        )
        print(f"  1. Run tests:  {venv_hint}cd abia-app && pytest")
        print("  2. Fast mode:  pytest --reuse-db --no-migrations -x")
        print("=" * 50)


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────


def main() -> int:
    """Application entry point."""
    project_root = Path.cwd()
    cli = TestEnvironmentCLI(project_root)
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
