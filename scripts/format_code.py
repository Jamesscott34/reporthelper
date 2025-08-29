#!/usr/bin/env python3
"""
Code formatting script for AI Report Writer.

This script runs all code quality tools in the correct order:
1. isort - Import sorting
2. black - Code formatting
3. flake8 - Linting
4. mypy - Type checking
5. bandit - Security scanning

Usage:
    python scripts/format_code.py [--check] [--fix]
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, check_mode=False):
    """Run a command and handle its output."""
    print(f"\n🔄 {description}...")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stdout.strip():
                print(f"   STDOUT: {result.stdout.strip()}")
            if result.stderr.strip():
                print(f"   STDERR: {result.stderr.strip()}")
            return False

    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def main():
    """Main function to run code quality checks."""
    parser = argparse.ArgumentParser(description="Run code quality tools")
    parser.add_argument(
        "--check", action="store_true", help="Check only, do not modify files"
    )
    parser.add_argument(
        "--fix", action="store_true", help="Fix issues automatically where possible"
    )

    args = parser.parse_args()

    print("🛠️  AI Report Writer - Code Quality Tools")
    print("=" * 50)

    # Determine mode
    check_mode = args.check
    fix_mode = args.fix or not check_mode

    if check_mode:
        print("🔍 Running in CHECK mode (no files will be modified)")
    else:
        print("🔧 Running in FIX mode (files will be formatted)")

    success_count = 0
    total_checks = 0

    # 1. Import sorting with isort
    total_checks += 1
    isort_cmd = "python -m isort ."
    if check_mode:
        isort_cmd += " --check-only --diff"

    if run_command(isort_cmd, "Import sorting (isort)", check_mode):
        success_count += 1

    # 2. Code formatting with black
    total_checks += 1
    black_cmd = "python -m black ."
    if check_mode:
        black_cmd += " --check --diff"

    if run_command(black_cmd, "Code formatting (black)", check_mode):
        success_count += 1

    # 3. Linting with flake8
    total_checks += 1
    if run_command("python -m flake8", "Code linting (flake8)", True):
        success_count += 1

    # 4. Type checking with mypy (optional, as it may not be fully configured)
    total_checks += 1
    if run_command(
        "python -m mypy breakdown ai_report_writer --ignore-missing-imports",
        "Type checking (mypy)",
        True,
    ):
        success_count += 1

    # 5. Security scanning with bandit
    total_checks += 1
    if run_command(
        "python -m bandit -r breakdown ai_report_writer -f json",
        "Security scanning (bandit)",
        True,
    ):
        success_count += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Code Quality Summary: {success_count}/{total_checks} checks passed")

    if success_count == total_checks:
        print("🎉 All code quality checks passed!")
        return 0
    else:
        print(f"⚠️  {total_checks - success_count} checks failed")
        if fix_mode and not check_mode:
            print("💡 Some issues may have been auto-fixed. Run again to verify.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
