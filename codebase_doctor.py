#!/usr/bin/env python3
"""
Codebase Doctor — Supercharged Audit for Django + Docker
Automatically finds and fixes issues in your codebase, with special love for 
Django dynamic fields and containerized environments.
"""

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import argparse
import time
import shutil

# Rich for pretty output (fallback to plain print)
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

# OpenAI optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Issue:
    file_path: str
    line: int
    column: Optional[int]
    severity: str  # 'error', 'warning', 'info'
    tool: str      # linter, compiler, test, etc.
    message: str
    fix_suggestion: Optional[str] = None
    category: str = "unknown"  # syntax, style, security, test, import, django


@dataclass
class AuditReport:
    issues: List[Issue] = field(default_factory=list)
    total_files: int = 0
    analyzed_files: int = 0
    test_results: Dict = field(default_factory=dict)
    ai_recommendation: Optional[str] = None
    fix_script_content: Optional[str] = None
    summary: str = ""


# ---------------------------------------------------------------------------
# Core Auditor Class
# ---------------------------------------------------------------------------

class CodebaseDoctor:
    def __init__(self, root_path: Path, use_ai: bool = False, model: str = "gpt-4",
                 auto_fix: bool = False, use_docker: bool = False, container_name: str = None):
        self.root = root_path.resolve()
        self.use_ai = use_ai and OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY")
        self.model = model
        self.auto_fix = auto_fix
        self.use_docker = use_docker
        self.container_name = container_name or self._detect_django_container()
        self.report = AuditReport()
        self.console = Console() if RICH_AVAILABLE else None
        self._setup_openai()
        self._setup_docker_prefix()

    def _setup_openai(self):
        if self.use_ai:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            if not openai.api_key:
                self.use_ai = False
                self._print("AI mode disabled: OPENAI_API_KEY not set", "warning")

    def _detect_django_container(self) -> Optional[str]:
        """Try to find a running container with manage.py or Django."""
        if not shutil.which('docker'):
            return None
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True, text=True
            )
            for name in result.stdout.splitlines():
                # Check if this container has manage.py
                check = subprocess.run(
                    ['docker', 'exec', name, 'test', '-f', '/app/manage.py'],
                    capture_output=True
                )
                if check.returncode == 0:
                    return name
        except Exception:
            pass
        return None

    def _setup_docker_prefix(self):
        """If using Docker, prefix commands with docker exec."""
        self.cmd_prefix = []
        if self.use_docker and self.container_name:
            self.cmd_prefix = ['docker', 'exec', '-i', self.container_name]
            self._print(f"Running commands inside container: {self.container_name}", "info")
        else:
            self.cmd_prefix = []

    def _run_command(self, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command, optionally inside Docker."""
        full_cmd = self.cmd_prefix + cmd
        return subprocess.run(full_cmd, **kwargs)

    def _print(self, msg: str, level: str = "info"):
        if self.console:
            if level == "error":
                self.console.print(f"[red]**ERROR**: {msg}[/red]")
            elif level == "warning":
                self.console.print(f"[yellow]**WARNING**: {msg}[/yellow]")
            elif level == "success":
                self.console.print(f"[green]{msg}[/green]")
            else:
                self.console.print(msg)
        else:
            print(msg)

    def run(self) -> AuditReport:
        """Main entry point."""
        self._print(Panel.fit("🧬 Codebase Doctor 🧬", style="bold magenta") if self.console else "=== Codebase Doctor ===")
        self._print(f"Scanning: {self.root}", "info")
        if self.use_docker and self.container_name:
            self._print(f"Using Docker container: {self.container_name}", "info")

        # Step 1: Discover files
        files = self._find_files()
        self.report.total_files = len(files)
        self._print(f"Found {len(files)} files to analyze.", "success")

        # Step 2: Syntax & import checking (fast)
        self._check_syntax(files)

        # Step 3: Run linters (pylint, flake8, mypy, bandit)
        self._run_linters(files)

        # Step 4: Run tests if any
        self._run_tests()

        # Step 5: Security audit
        self._run_security(files)

        # Step 6: Django-specific checks
        self._run_django_checks()

        # Step 7: Dynamic field checks (JSONField, etc.)
        self._check_dynamic_fields(files)

        # Step 8: Generate AI fix plan
        if self.use_ai and self.report.issues:
            self._generate_ai_fix_plan()

        # Step 9: Generate auto-fix script
        self._generate_fix_script()

        # Step 10: Generate summary
        self._generate_summary()

        return self.report

    def _find_files(self) -> List[Path]:
        """Recursively find relevant source files."""
        extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.go', '.rs'}
        ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', 'env', 'dist', 'build', 'target'}
        files = []
        for path in self.root.rglob('*'):
            if path.is_file() and path.suffix in extensions:
                if not any(part in ignore_dirs for part in path.parts):
                    files.append(path)
        return files

    def _check_syntax(self, files: List[Path]):
        self._print("🔍 Checking syntax and imports...", "info")
        for file in files:
            if file.suffix == '.py':
                try:
                    ast.parse(file.read_text(encoding='utf-8'))
                except SyntaxError as e:
                    self.report.issues.append(Issue(
                        file_path=str(file),
                        line=e.lineno or 0,
                        column=e.offset,
                        severity="error",
                        tool="syntax",
                        message=str(e),
                        category="syntax"
                    ))
                except Exception as e:
                    self.report.issues.append(Issue(
                        file_path=str(file),
                        line=0,
                        column=None,
                        severity="error",
                        tool="syntax",
                        message=f"Unexpected error: {e}",
                        category="syntax"
                    ))

    def _run_linters(self, files: List[Path]):
        self._print("🧹 Running linters...", "info")
        py_files = [f for f in files if f.suffix == '.py']
        if not py_files:
            return

        # Flake8
        try:
            cmd = ['flake8', '--max-line-length=120', '--format=json'] + [str(f) for f in py_files]
            result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root))
            if result.stdout:
                data = json.loads(result.stdout)
                for file, issues in data.items():
                    for issue in issues:
                        self.report.issues.append(Issue(
                            file_path=file,
                            line=issue.get('line_number', 0),
                            column=issue.get('column_number', 0),
                            severity="warning" if issue.get('code', '').startswith('W') else "error",
                            tool="flake8",
                            message=f"{issue['code']}: {issue['text']}",
                            category="style"
                        ))
        except (FileNotFoundError, json.JSONDecodeError):
            self._print("flake8 not installed or failed; skipping.", "warning")

        # Mypy
        try:
            cmd = ['mypy', '--no-color', '--no-error-summary'] + [str(f) for f in py_files]
            result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root))
            for line in result.stdout.splitlines():
                if ':' in line and ' error: ' in line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        file = parts[0]
                        line_num = int(parts[1]) if parts[1].isdigit() else 0
                        msg = ':'.join(parts[2:]).strip()
                        self.report.issues.append(Issue(
                            file_path=file,
                            line=line_num,
                            column=None,
                            severity="error",
                            tool="mypy",
                            message=msg,
                            category="type"
                        ))
        except FileNotFoundError:
            self._print("mypy not installed; skipping.", "warning")

    def _run_tests(self):
        self._print("🧪 Running test suite...", "info")
        test_results = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "details": []}
        test_dirs = ['tests', 'test', 'testing']
        found_test = any((self.root / d).exists() for d in test_dirs)
        if not found_test:
            self._print("No test directory found; skipping tests.", "warning")
            self.report.test_results = test_results
            return

        try:
            cmd = ['pytest', '--json-report', '--json-report-file=report.json', '-v', '--tb=short']
            result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root), timeout=120)
            report_file = self.root / 'report.json'
            if report_file.exists():
                try:
                    data = json.loads(report_file.read_text())
                    test_results['passed'] = data.get('summary', {}).get('passed', 0)
                    test_results['failed'] = data.get('summary', {}).get('failed', 0)
                    test_results['errors'] = data.get('summary', {}).get('errors', 0)
                    test_results['skipped'] = data.get('summary', {}).get('skipped', 0)
                    for test in data.get('tests', []):
                        if test.get('outcome') in ('failed', 'error'):
                            test_results['details'].append({
                                'name': test.get('nodeid', ''),
                                'outcome': test.get('outcome'),
                                'message': test.get('call', {}).get('crash', {}).get('message', '')
                            })
                    report_file.unlink(missing_ok=True)
                except Exception:
                    pass
            else:
                # fallback parse
                for line in result.stdout.splitlines():
                    if 'PASSED' in line:
                        test_results['passed'] += 1
                    elif 'FAILED' in line:
                        test_results['failed'] += 1
                    elif 'ERROR' in line:
                        test_results['errors'] += 1
                    elif 'SKIPPED' in line:
                        test_results['skipped'] += 1
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._print("pytest not found or timed out; trying unittest.", "warning")
            try:
                cmd = ['python', '-m', 'unittest', 'discover', '-v']
                result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root), timeout=120)
                for line in result.stdout.splitlines():
                    if ' ... ok' in line:
                        test_results['passed'] += 1
                    elif ' ... FAIL' in line:
                        test_results['failed'] += 1
                    elif ' ... ERROR' in line:
                        test_results['errors'] += 1
                    elif ' ... skipped' in line:
                        test_results['skipped'] += 1
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self._print("unittest not found; skipping tests.", "warning")

        self.report.test_results = test_results
        self._print(f"Tests: {test_results['passed']} passed, {test_results['failed']} failed, {test_results['errors']} errors, {test_results['skipped']} skipped.", "info")

        for detail in test_results['details']:
            self.report.issues.append(Issue(
                file_path="test",
                line=0,
                column=None,
                severity="error",
                tool="pytest",
                message=f"Test failed: {detail['name']} - {detail['message']}",
                category="test"
            ))

    def _run_security(self, files: List[Path]):
        self._print("🔒 Running security audit...", "info")
        py_files = [f for f in files if f.suffix == '.py']
        if not py_files:
            return
        try:
            cmd = ['bandit', '-r', '-f', 'json'] + [str(f) for f in py_files]
            result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root))
            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    self.report.issues.append(Issue(
                        file_path=issue.get('filename', ''),
                        line=issue.get('line_number', 0),
                        column=None,
                        severity=issue.get('issue_severity', 'MEDIUM').lower(),
                        tool="bandit",
                        message=f"{issue['test_name']}: {issue['issue_text']}",
                        category="security"
                    ))
        except (FileNotFoundError, json.JSONDecodeError):
            self._print("bandit not installed or failed; skipping.", "warning")

    def _run_django_checks(self):
        """Run Django's system checks and migration checks."""
        manage_py = self.root / 'manage.py'
        if not manage_py.exists():
            return

        self._print("🐍 Running Django system checks...", "info")
        try:
            cmd = ['python', 'manage.py', 'check', '--deploy']
            result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root))
            for line in result.stdout.splitlines():
                if 'ERROR' in line or 'WARNING' in line:
                    self.report.issues.append(Issue(
                        file_path="Django check",
                        line=0,
                        column=None,
                        severity="error" if 'ERROR' in line else "warning",
                        tool="django",
                        message=line,
                        category="framework"
                    ))
        except Exception as e:
            self._print(f"Django check failed: {e}", "warning")

        # Migration check
        self._print("📦 Checking migrations...", "info")
        try:
            cmd = ['python', 'manage.py', 'makemigrations', '--check', '--dry-run']
            result = self._run_command(cmd, capture_output=True, text=True, cwd=str(self.root))
            if result.returncode != 0:
                self.report.issues.append(Issue(
                    file_path="migrations",
                    line=0,
                    column=None,
                    severity="error",
                    tool="django",
                    message="Pending migrations detected. Run makemigrations.",
                    category="framework"
                ))
        except Exception as e:
            self._print(f"Migration check failed: {e}", "warning")

    def _check_dynamic_fields(self, files: List[Path]):
        """Look for potential issues with dynamic fields (JSONField, etc.)."""
        self._print("🧩 Checking dynamic fields...", "info")
        for file in files:
            if file.suffix == '.py':
                try:
                    content = file.read_text(encoding='utf-8')
                    # Detect JSONField, JSONField, HStoreField, etc.
                    if re.search(r'JSONField|HStoreField', content):
                        # Check if they are used safely (e.g., with default)
                        if not re.search(r'default\s*=', content) and not re.search(r'blank\s*=\s*True', content):
                            self.report.issues.append(Issue(
                                file_path=str(file),
                                line=0,
                                column=None,
                                severity="warning",
                                tool="dynamic_fields",
                                message="JSONField or HStoreField without default/blank might cause database errors.",
                                category="database"
                            ))
                        # Check for potential security (raw input)
                        if re.search(r'request\.(GET|POST|data)', content) and re.search(r'\.save\(\)', content):
                            self.report.issues.append(Issue(
                                file_path=str(file),
                                line=0,
                                column=None,
                                severity="warning",
                                tool="dynamic_fields",
                                message="Possible unsafe JSONField assignment from request data. Validate input.",
                                category="security"
                            ))
                except Exception:
                    pass

    def _generate_ai_fix_plan(self):
        self._print("🤖 Generating AI fix plan...", "info")
        if not self.report.issues:
            return

        issue_summary = "\n".join([
            f"- {i.file_path}:{i.line} [{i.severity}] {i.tool}: {i.message}"
            for i in self.report.issues[:50]
        ])

        prompt = f"""
You are an expert Django developer. Below are issues found in a codebase.

Please provide a detailed fix plan prioritizing critical errors. Include root causes and concrete steps. Format as Markdown with sections: Overview, Critical Fixes, Additional Improvements, Step-by-Step Plan.

Issues: {issue_summary}

Also include potential pitfalls and how to avoid them.
"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that produces detailed, actionable code fixes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            self.report.ai_recommendation = response.choices[0].message.content
            self._print("AI fix plan generated successfully.", "success")
        except Exception as e:
            self._print(f"AI generation failed: {e}", "error")

    def _generate_fix_script(self):
        self._print("📝 Generating fix script...", "info")
        script_lines = ["#!/bin/bash", "# Auto-generated fix script by Codebase Doctor", ""]
        fix_steps = []

        if self.auto_fix:
            fix_steps.append("echo 'Running isort...'")
            fix_steps.append("isort . --profile black 2>/dev/null || true")
            fix_steps.append("echo 'Running black...'")
            fix_steps.append("black . 2>/dev/null || true")
            fix_steps.append("echo 'Running autopep8...'")
            fix_steps.append("autopep8 --in-place --recursive . 2>/dev/null || true")
            fix_steps.append("echo 'Running Django migrations if needed...'")
            fix_steps.append("python manage.py makemigrations 2>/dev/null || true")
            fix_steps.append("python manage.py migrate 2>/dev/null || true")

            fix_steps.append("echo 'Running tests to verify fixes...'")
            fix_steps.append("pytest 2>/dev/null || true")

        script_lines.extend(fix_steps)
        script_lines.append("echo 'Fix script completed.'")

        self.report.fix_script_content = "\n".join(script_lines)

    def _generate_summary(self):
        issues_by_severity = {"error": 0, "warning": 0, "info": 0}
        for issue in self.report.issues:
            issues_by_severity[issue.severity] = issues_by_severity.get(issue.severity, 0) + 1

        summary = f"""
# Codebase Audit Summary
Total files scanned: {self.report.total_files}
Issues found: {len(self.report.issues)}
    Errors: {issues_by_severity.get('error', 0)}
    Warnings: {issues_by_severity.get('warning', 0)}
    Info: {issues_by_severity.get('info', 0)}

Tests: {self.report.test_results.get('passed', 0)} passed, {self.report.test_results.get('failed', 0)} failed, {self.report.test_results.get('errors', 0)} errors.

Auto-fix script generated (use --fix to execute).
"""
        if self.report.ai_recommendation:
            summary += "\nAI Fix Plan:\n" + self.report.ai_recommendation

        self.report.summary = summary
        self._print(summary)

    def export_report(self, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        # JSON
        json_path = output_dir / "audit_report.json"
        with open(json_path, 'w') as f:
            json.dump({
                "issues": [vars(i) for i in self.report.issues],
                "test_results": self.report.test_results,
                "summary": self.report.summary,
                "ai_recommendation": self.report.ai_recommendation,
                "fix_script": self.report.fix_script_content
            }, f, indent=2)
        self._print(f"JSON report saved to {json_path}")

        # Markdown
        md_path = output_dir / "audit_report.md"
        with open(md_path, 'w') as f:
            f.write(f"# Codebase Audit Report\n\n{self.report.summary}\n\n")
            f.write("## Detailed Issues\n\n")
            for issue in self.report.issues:
                f.write(f"- **{issue.file_path}**:{issue.line} [{issue.severity}] {issue.tool}: {issue.message}\n")
            if self.report.ai_recommendation:
                f.write("\n## AI Fix Plan\n\n")
                f.write(self.report.ai_recommendation)
            if self.report.fix_script_content:
                f.write("\n\n## Auto-fix Script\n\n```bash\n")
                f.write(self.report.fix_script_content)
                f.write("\n```\n")
        self._print(f"Markdown report saved to {md_path}")

        if self.report.fix_script_content:
            script_path = output_dir / "fix_script.sh"
            script_path.write_text(self.report.fix_script_content)
            script_path.chmod(0o755)
            self._print(f"Fix script saved to {script_path} (chmod +x)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description="Codebase Doctor - Audit and Fix")
    parser.add_argument("--path", type=str, default=".", help="Path to codebase root")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-fix (runs formatting tools)")
    parser.add_argument("--ai", action="store_true", help="Use OpenAI to generate fix plan (requires API key)")
    parser.add_argument("--model", type=str, default="gpt-4", help="OpenAI model to use")
    parser.add_argument("--output", type=str, default="./audit_output", help="Output directory for reports")
    parser.add_argument("--no-rich", action="store_true", help="Disable rich output")
    parser.add_argument("--docker", action="store_true", help="Run commands inside a Django Docker container")
    parser.add_argument("--container", type=str, help="Specify container name (auto-detected if not given)")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.no_rich:
        global RICH_AVAILABLE
        RICH_AVAILABLE = False

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: path {root} does not exist.")
        sys.exit(1)

    doctor = CodebaseDoctor(
        root_path=root,
        use_ai=args.ai,
        model=args.model,
        auto_fix=args.fix,
        use_docker=args.docker,
        container_name=args.container
    )
    report = doctor.run()
    doctor.export_report(Path(args.output))
    print("\n✅ Done. Review the reports in", args.output)


if __name__ == "__main__":
    main()
