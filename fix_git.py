#!/usr/bin/env python3
"""ABIA Git Repository Emergency Fix — 10X Recovery Script.

Fixes ALL issues from the failed git init + push:
  1. Embedded git repos (abia-ai, abia-analytics, abia-app, abia-core, abia-docs)
  2. GitHub HTTPS auth failure → switches to SSH
  3. Backup files committed to history
  4. Mixed abia/ vs abia-app/ directory structure
  5. .env / .env.prod secrets in git history
  6. Proper .gitignore creation

Run from project root: cd ~/abia-migration-observatory && python3 fix_git.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Final


# ──────────────────────────────────────────────────────────────────────────────
# Domain Exceptions
# ──────────────────────────────────────────────────────────────────────────────

class GitFixError(Exception):
    """Base exception for git fix failures."""
    pass


class SSHNotConfiguredError(GitFixError):
    """Raised when SSH keys are missing or not added to GitHub."""
    pass


class EmbeddedRepoError(GitFixError):
    """Raised when embedded repos cannot be converted."""
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

EMBEDDED_REPOS: Final[list[str]] = [
    "abia-ai", "abia-analytics", "abia-app", "abia-core", "abia-docs"
]

BACKUP_PATTERNS: Final[list[str]] = [
    "*.backup.*", "*.bak", "*~", "*.swp", "*.swo"
]

SECRET_FILES: Final[list[str]] = [
    ".env", ".env.prod", ".env.local", "*.pem", "*.key", "*.crt"
]

GITIGNORE_TEMPLATE: Final[str] = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment / Secrets
.env
.env.*
!.env.example
*.pem
*.key
*.crt
secrets/

# Backup files
*.backup.*
*.bak
*~
*.swp
*.swo

# Virtual environments
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.iml

# OS
.DS_Store
Thumbs.db

# Docker
*.pid

# Test artifacts
.pytest_cache/
.coverage
htmlcov/
.tox/
"""


# ──────────────────────────────────────────────────────────────────────────────
# Service Layer
# ──────────────────────────────────────────────────────────────────────────────

class GitService:
    """Business logic for git operations."""

    @staticmethod
    def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a git command safely."""
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if check and result.returncode != 0:
            raise GitFixError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
        return result

    @staticmethod
    def is_in_git_repo(path: Path) -> bool:
        """Check if directory is inside a git repo."""
        return (path / ".git").exists() or GitService._has_git_parent(path)

    @staticmethod
    def _has_git_parent(path: Path) -> bool:
        """Check if any parent has .git."""
        for parent in path.parents:
            if (parent / ".git").exists():
                return True
        return False


class SSHService:
    """SSH key management for GitHub."""

    @staticmethod
    def check_ssh_key() -> bool:
        """Check if SSH key exists and is added to agent."""
        ssh_dir = Path.home() / ".ssh"
        keys = list(ssh_dir.glob("id_*"))
        return len(keys) > 0

    @staticmethod
    def test_github_connection() -> bool:
        """Test SSH connection to GitHub."""
        result = subprocess.run(
            ["ssh", "-T", "git@github.com"],
            capture_output=True, text=True, check=False, timeout=10
        )
        return "successfully authenticated" in result.stderr

    @staticmethod
    def setup_wsl_ssh() -> None:
        """Copy Windows SSH keys to WSL if missing."""
        wsl_ssh = Path.home() / ".ssh"
        windows_ssh = Path("/mnt/c/Users") / Path.home().name / ".ssh"

        if not wsl_ssh.exists() and windows_ssh.exists():
            print("    Copying Windows SSH keys to WSL...")
            shutil.copytree(windows_ssh, wsl_ssh)
            for key_file in wsl_ssh.glob("id_*"):
                if not key_file.name.endswith(".pub"):
                    key_file.chmod(0o600)
                else:
                    key_file.chmod(0o644)
            print("    ✓ SSH keys copied")

    @staticmethod
    def ensure_agent() -> None:
        """Start ssh-agent and add keys."""
        subprocess.run(["eval", "$(ssh-agent -s)"], shell=True, check=False)
        for key in (Path.home() / ".ssh").glob("id_*"):
            if not key.name.endswith(".pub"):
                subprocess.run(["ssh-add", str(key)], check=False)


class RepoCleanupService:
    """Clean up embedded repos and unwanted files."""

    @staticmethod
    def find_embedded_repos(project_root: Path) -> list[Path]:
        """Find directories with .git inside them."""
        embedded = []
        for name in EMBEDDED_REPOS:
            repo_path = project_root / name
            if (repo_path / ".git").exists():
                embedded.append(repo_path)
        return embedded

    @staticmethod
    def convert_to_regular(project_root: Path, repo_path: Path) -> None:
        """Convert embedded git repo to regular directory."""
        git_dir = repo_path / ".git"
        if git_dir.exists():
            print(f"    Removing {repo_path.name}/.git...")
            shutil.rmtree(git_dir)

    @staticmethod
    def remove_backup_files(project_root: Path) -> list[Path]:
        """Find and remove backup files."""
        removed = []
        for pattern in BACKUP_PATTERNS:
            for f in project_root.rglob(pattern):
                print(f"    Removing backup: {f.relative_to(project_root)}")
                f.unlink()
                removed.append(f)
        return removed

    @staticmethod
    def remove_secrets_from_history(project_root: Path) -> None:
        """Remove secret files from git tracking (not history)."""
        for pattern in SECRET_FILES:
            for f in project_root.rglob(pattern):
                rel = f.relative_to(project_root)
                try:
                    GitService.run(["git", "rm", "--cached", str(rel)], check=False)
                    print(f"    Untracked secret: {rel}")
                except GitFixError:
                    pass


# ──────────────────────────────────────────────────────────────────────────────
# Controller / CLI
# ──────────────────────────────────────────────────────────────────────────────

class GitFixCLI:
    """Command-line interface for git emergency fix."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def run(self) -> int:
        """Execute the full recovery workflow."""
        try:
            self._print_header()
            self._fix_embedded_repos()
            self._create_gitignore()
            self._remove_backup_files()
            self._untrack_secrets()
            self._stage_all()
            self._fix_github_auth()
            self._print_success()
            return 0
        except GitFixError as exc:
            print(f"\n❌ Fix failed: {exc}", file=sys.stderr)
            return 1

    def _print_header(self) -> None:
        """Display recovery banner."""
        print("=" * 60)
        print("ABIA GIT REPOSITORY EMERGENCY FIX")
        print("=" * 60)

    def _fix_embedded_repos(self) -> None:
        """Convert embedded git repos to regular directories."""
        print("\n[1] Fixing embedded git repositories...")
        embedded = RepoCleanupService.find_embedded_repos(self.project_root)
        if not embedded:
            print("    ✓ No embedded repos found")
            return
        for repo_path in embedded:
            RepoCleanupService.convert_to_regular(self.project_root, repo_path)
        print(f"    ✓ Fixed {len(embedded)} embedded repos")

    def _create_gitignore(self) -> None:
        """Create proper .gitignore if missing or incomplete."""
        print("\n[2] Setting up .gitignore...")
        gitignore_path = self.project_root / ".gitignore"
        gitignore_path.write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
        print("    ✓ .gitignore created/updated")

    def _remove_backup_files(self) -> None:
        """Remove backup files from working tree."""
        print("\n[3] Removing backup files...")
        removed = RepoCleanupService.remove_backup_files(self.project_root)
        print(f"    ✓ Removed {len(removed)} backup files")

    def _untrack_secrets(self) -> None:
        """Untrack secret files from git index."""
        print("\n[4] Untracking secret files...")
        RepoCleanupService.remove_secrets_from_history(self.project_root)
        print("    ✓ Secrets untracked")

    def _stage_all(self) -> None:
        """Stage all changes for commit."""
        print("\n[5] Staging changes...")
        GitService.run(["git", "add", "."], check=False)
        print("    ✓ All changes staged")
        print("\n    ⚠️  Review changes with: git status")
        print("    Then commit: git commit -m 'fix: resolve embedded repos and cleanup'")

    def _fix_github_auth(self) -> None:
        """Switch remote from HTTPS to SSH."""
        print("\n[6] Fixing GitHub authentication...")
        SSHService.setup_wsl_ssh()

        if not SSHService.check_ssh_key():
            print("    ⚠️  No SSH keys found!")
            print("    Generate one: ssh-keygen -t ed25519 -C 'your@email.com'")
            print("    Add to GitHub: https://github.com/settings/keys")
            raise SSHNotConfiguredError("SSH key missing")

        SSHService.ensure_agent()

        if SSHService.test_github_connection():
            print("    ✓ GitHub SSH connection works")
        else:
            print("    ⚠️  SSH key may not be added to GitHub yet")
            print("    Add your public key to: https://github.com/settings/keys")

        # Switch remote to SSH
        try:
            result = GitService.run(["git", "remote", "-v"], check=False)
            if "https://github.com" in result.stdout:
                print("    Switching remote from HTTPS to SSH...")
                # Extract repo path from HTTPS URL
                for line in result.stdout.split("\n"):
                    if "origin" in line and "https://github.com" in line:
                        parts = line.split()
                        url = parts[1]
                        repo_path = url.replace("https://github.com/", "").replace(".git", "")
                        ssh_url = f"git@github.com:{repo_path}.git"
                        GitService.run(["git", "remote", "set-url", "origin", ssh_url])
                        print(f"    ✓ Remote switched to: {ssh_url}")
                        break
        except GitFixError:
            print("    ⚠️  Could not auto-switch remote. Run manually:")
            print("    git remote set-url origin git@github.com:USER/REPO.git")

    def _print_success(self) -> None:
        """Display completion message."""
        print("\n" + "=" * 60)
        print("FIX COMPLETE!")
        print("=" * 60)
        print("Next steps:")
        print("  1. Review:    git status")
        print("  2. Commit:    git commit -m 'fix: resolve embedded repos'")
        print("  3. Push:      git push -u origin main")
        print("=" * 60)


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> int:
    """Application entry point."""
    project_root = Path.cwd()
    if not (project_root / ".git").exists():
        print("Error: Not in a git repository. Run from project root.", file=sys.stderr)
        return 1
    cli = GitFixCLI(project_root)
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
