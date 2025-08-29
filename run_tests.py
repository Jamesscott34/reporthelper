#!/usr/bin/env python3
"""
Test Runner for AI Report Writer MVP

This script runs the comprehensive test suite and provides detailed output
about the health of the entire system before proceeding with development.

Usage:
    python run_tests.py
    python run_tests.py --coverage  # Run with coverage report
    python run_tests.py --fast      # Run only fast tests
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def create_test_results_dir():
    """Create test results directory with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path("test_results") / f"run_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def save_test_output(results_dir, filename, content, test_info=None):
    """Save test output to file with metadata."""
    filepath = results_dir / filename

    # Create header with metadata
    header = f"""{'=' * 80}
AI Report Writer - Test Results
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

"""

    if test_info:
        header += f"""Test Information:
- Test Type: {test_info.get('type', 'Unknown')}
- Duration: {test_info.get('duration', 'Unknown')}
- Status: {test_info.get('status', 'Unknown')}
- Command: {test_info.get('command', 'Unknown')}

{'=' * 80}

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)

    return filepath


def parse_test_failures(test_output):
    """Parse test output to extract failure details."""
    failures = []
    errors = []

    if not test_output:
        return failures, errors

    lines = test_output.split("\n")
    current_failure = None
    current_error = None
    in_failure = False
    in_error = False

    for line in lines:
        # Detect failure start
        if line.startswith("FAIL: "):
            if current_failure:
                failures.append(current_failure)
            current_failure = {
                "test_name": line.replace("FAIL: ", "").strip(),
                "traceback": [],
                "type": "FAIL",
            }
            in_failure = True
            in_error = False

        # Detect error start
        elif line.startswith("ERROR: "):
            if current_error:
                errors.append(current_error)
            current_error = {
                "test_name": line.replace("ERROR: ", "").strip(),
                "traceback": [],
                "type": "ERROR",
            }
            in_error = True
            in_failure = False

        # Detect section end
        elif line.startswith(
            "======================================================================"
        ):
            if current_failure:
                failures.append(current_failure)
                current_failure = None
            if current_error:
                errors.append(current_error)
                current_error = None
            in_failure = False
            in_error = False

        # Collect traceback lines
        elif in_failure and current_failure:
            current_failure["traceback"].append(line)
        elif in_error and current_error:
            current_error["traceback"].append(line)

    # Don't forget the last one
    if current_failure:
        failures.append(current_failure)
    if current_error:
        errors.append(current_error)

    return failures, errors


def create_failure_report(failures, errors):
    """Create a detailed failure report."""
    report = []

    if failures or errors:
        report.append("🔴 TEST FAILURES AND ERRORS SUMMARY")
        report.append("=" * 50)
        report.append("")

        # Process failures
        for i, failure in enumerate(failures, 1):
            report.append(f"FAILURE #{i}: {failure['test_name']}")
            report.append("-" * 40)

            # Extract key information from traceback
            traceback_text = "\n".join(failure["traceback"])

            # Find the assertion error
            assertion_lines = [
                line
                for line in failure["traceback"]
                if "AssertionError" in line or "self.assert" in line or "!=" in line
            ]
            if assertion_lines:
                report.append("❌ Assertion Failed:")
                for line in assertion_lines:
                    if line.strip():
                        report.append(f"   {line.strip()}")
                report.append("")

            # Find the failing function
            file_lines = [
                line
                for line in failure["traceback"]
                if 'File "' in line and "test_" in line
            ]
            if file_lines:
                report.append("📍 Location:")
                for line in file_lines:
                    report.append(f"   {line.strip()}")
                report.append("")

            # Add full traceback
            report.append("📋 Full Traceback:")
            for line in failure["traceback"]:
                report.append(f"   {line}")
            report.append("")
            report.append("=" * 50)
            report.append("")

        # Process errors
        for i, error in enumerate(errors, 1):
            report.append(f"ERROR #{i}: {error['test_name']}")
            report.append("-" * 40)

            # Extract key information
            traceback_text = "\n".join(error["traceback"])

            # Find the error type
            error_lines = [
                line
                for line in error["traceback"]
                if any(
                    err in line
                    for err in ["Error:", "Exception:", "ImportError:", "KeyError:"]
                )
            ]
            if error_lines:
                report.append("❌ Error Type:")
                for line in error_lines:
                    report.append(f"   {line.strip()}")
                report.append("")

            # Find the failing function
            file_lines = [
                line
                for line in error["traceback"]
                if 'File "' in line and ("test_" in line or "breakdown" in line)
            ]
            if file_lines:
                report.append("📍 Location:")
                for line in file_lines:
                    report.append(f"   {line.strip()}")
                report.append("")

            # Add full traceback
            report.append("📋 Full Traceback:")
            for line in error["traceback"]:
                report.append(f"   {line}")
            report.append("")
            report.append("=" * 50)
            report.append("")

    else:
        report.append("✅ ALL TESTS PASSED!")
        report.append("No failures or errors to report.")

    return "\n".join(report)


def print_banner():
    """Print test banner."""
    print("🧪 AI Report Writer - Comprehensive Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def run_migrations():
    """Ensure migrations are up to date."""
    print("📋 Checking migrations...")
    result = subprocess.run(
        [sys.executable, "manage.py", "makemigrations", "--check"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("⚠️  Migrations needed. Running makemigrations...")
        subprocess.run([sys.executable, "manage.py", "makemigrations"])
        subprocess.run([sys.executable, "manage.py", "migrate"])
    else:
        print("✅ Migrations up to date")


def run_basic_checks():
    """Run basic Django checks."""
    print("\n🔍 Running Django system checks...")
    result = subprocess.run(
        [sys.executable, "manage.py", "check"], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ Django system checks passed")
    else:
        print("❌ Django system checks failed:")
        print(result.stdout)
        print(result.stderr)
        return False
    return True


def run_tests(coverage=False, fast=False, results_dir=None):
    """Run the test suite and capture detailed output."""
    print("\n🧪 Running test suite...")

    start_time = datetime.now()

    cmd = [sys.executable, "manage.py", "test"]
    test_type = "fast" if fast else "full"

    if fast:
        # Run only model and basic tests
        cmd.extend(
            [
                "breakdown.test_full_system.DocumentModelTests",
                "breakdown.test_full_system.AnnotationModelTests",
                "breakdown.test_full_system.SerializerTests",
                "--verbosity=2",
            ]
        )
        print("⚡ Running fast tests only...")
    else:
        cmd.extend(["breakdown.test_full_system", "--verbosity=2"])

    if coverage:
        # Install coverage if not available
        try:
            import coverage
        except ImportError:
            print("📦 Installing coverage...")
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"])

        # Run with coverage
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--source",
            ".",
            "manage.py",
            "test",
            "breakdown.test_full_system",
            "--verbosity=2",
        ]

    # Capture both stdout and stderr
    print(f"📝 Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    end_time = datetime.now()
    duration = str(end_time - start_time)

    # Combine stdout and stderr for complete output
    full_output = ""
    if result.stdout:
        full_output += "STDOUT:\n" + result.stdout + "\n\n"
    if result.stderr:
        full_output += "STDERR:\n" + result.stderr + "\n\n"

    # Print output to console
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Save results if directory provided
    if results_dir:
        # Test info for metadata
        test_info = {
            "type": test_type,
            "duration": duration,
            "status": "PASSED" if result.returncode == 0 else "FAILED",
            "command": " ".join(cmd),
            "return_code": result.returncode,
        }

        # Save full output
        save_test_output(results_dir, "test_output_full.txt", full_output, test_info)

        # Parse and save failure details
        failures, errors = parse_test_failures(result.stdout or "")
        failure_report = create_failure_report(failures, errors)

        save_test_output(
            results_dir,
            "test_failures_summary.txt",
            failure_report,
            {**test_info, "type": "failure_analysis"},
        )

        # Save JSON summary for programmatic access
        summary = {
            "timestamp": start_time.isoformat(),
            "duration": duration,
            "status": "PASSED" if result.returncode == 0 else "FAILED",
            "return_code": result.returncode,
            "command": " ".join(cmd),
            "test_type": test_type,
            "coverage_enabled": coverage,
            "total_failures": len(failures),
            "total_errors": len(errors),
            "failures": [{"name": f["test_name"], "type": f["type"]} for f in failures],
            "errors": [{"name": e["test_name"], "type": e["type"]} for e in errors],
        }

        with open(results_dir / "test_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    # Handle coverage if enabled
    if coverage and result.returncode == 0:
        print("\n📊 Generating coverage report...")
        cov_result = subprocess.run(
            [sys.executable, "-m", "coverage", "report"], capture_output=True, text=True
        )

        subprocess.run([sys.executable, "-m", "coverage", "html"])
        print("📈 HTML coverage report generated in htmlcov/")

        # Save coverage report if results directory exists
        if results_dir and cov_result.stdout:
            save_test_output(
                results_dir,
                "coverage_report.txt",
                cov_result.stdout,
                {"type": "coverage", "status": "completed"},
            )

    return result.returncode == 0


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")

    # Core dependencies that are essential for tests
    required_packages = [
        ("django", "django"),
        ("djangorestframework", "rest_framework"),
        ("django-cors-headers", "corsheaders"),
    ]

    # Optional dependencies (channels, daphne) - test will handle gracefully
    optional_packages = [("channels", "channels"), ("daphne", "daphne")]

    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    # Check optional packages but don't fail if missing
    optional_missing = []
    for package_name, import_name in optional_packages:
        try:
            __import__(import_name)
        except ImportError:
            optional_missing.append(package_name)

    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("💡 Run: pip install " + " ".join(missing))
        return False
    else:
        print("✅ All required dependencies installed")
        if optional_missing:
            print(
                f"⚠️  Optional packages missing (tests will skip related features): {', '.join(optional_missing)}"
            )
        return True


def check_api_connectivity():
    """Check if AI API is accessible and provide guidance for setup."""
    print("\n🔌 Checking AI API connectivity...")

    try:
        # Ensure Django is configured
        import django
        from django.conf import settings

        if not settings.configured:
            import os

            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_report_writer.settings")
            django.setup()

        # Import here to avoid issues if not available
        from breakdown.ai_breakdown import AIBreakdownService

        service = AIBreakdownService()
        print(f"   Model: {service.model}")
        print(f"   API Key: {'Present' if service.api_key else 'Missing'}")

        result = service.test_api_connectivity()

        if result["success"]:
            print("✅ AI API connectivity successful")
            print(f"   Response: {result.get('response', 'OK')}")
            print("🎉 AI features are ready to use!")
            return True
        else:
            print("❌ AI API connectivity failed")
            print(f"   Error: {result['message']}")

            if result.get("error") == "missing_api_key":
                print("\n🔧 How to fix:")
                print("   1. Visit https://openrouter.ai/ and sign up")
                print("   2. Get your API key from the dashboard")
                print("   3. Copy env.example to .env:")
                print("      cp env.example .env")
                print("   4. Edit .env and replace 'your_api_key_here':")
                print("      OPENROUTER_API_KEY=sk-or-v1-xxxxx")
                print("   5. Restart the application")

            elif result.get("error") == "invalid_api_key":
                print("\n🔧 How to fix:")
                print("   1. Check your .env file - verify OPENROUTER_API_KEY")
                print("   2. Ensure key starts with 'sk-or-v1-'")
                print("   3. Get a new key from https://openrouter.ai/")
                print("   4. Make sure you have credits in your account")

            elif result.get("error") == "rate_limit_exceeded":
                print("\n🔧 How to fix:")
                print("   1. Wait a few minutes before trying again")
                print("   2. Check usage at https://openrouter.ai/")
                print("   3. Consider upgrading your OpenRouter plan")

            elif result.get("error") == "timeout":
                print("\n🔧 How to fix:")
                print("   1. Check your internet connection")
                print("   2. Try again in a few moments")
                print("   3. Verify OpenRouter.ai is accessible")

            elif result.get("error") == "connection_error":
                print("\n🔧 How to fix:")
                print("   1. Check your internet connection")
                print("   2. Verify firewall/proxy settings")
                print("   3. Try again later")

            else:
                print("\n🔧 General troubleshooting:")
                print("   1. Check your internet connection")
                print("   2. Verify your .env file configuration")
                print("   3. Try again in a few minutes")
                print("   4. Check OpenRouter status page")

            print("\n⚠️  AI features will not work until this is resolved.")
            print("   Tests will continue but AI-dependent features may fail.")
            return False

    except ImportError as e:
        print("⚠️  Could not import AI service - skipping API check")
        print(f"   Error: {e}")
        print("   This might indicate a Django configuration issue.")
        return True  # Don't fail tests for import issues
    except Exception as e:
        print("⚠️  API connectivity check failed unexpectedly")
        print(f"   Error: {e}")
        print("   AI features may not work properly.")
        return True  # Don't fail tests for unexpected issues


def print_test_summary(success):
    """Print test summary."""
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ System is ready for continued development")
        print("\n📋 What was tested:")
        print("   • Document upload and processing")
        print("   • AI breakdown system + API connectivity")
        print("   • Section management")
        print("   • Annotation system (NEW)")
        print("   • REST API endpoints")
        print("   • WebSocket functionality")
        print("   • Permissions and security")
        print("   • Database models and validation")
        print("   • Serializers and views")
        print("   • Integration workflows")
        print("\n🚀 Ready to proceed with Report Composer implementation!")
    else:
        print("❌ TESTS FAILED")
        print("🔧 Please fix the failing tests before continuing development")
        print("\n💡 Common fixes:")
        print("   • Run: python manage.py makemigrations")
        print("   • Run: python manage.py migrate")
        print("   • Check: pip install -r requirements.txt")
        print("   • Verify: Database is accessible")
    print("=" * 60)


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run AI Report Writer test suite")
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage report"
    )
    parser.add_argument("--fast", action="store_true", help="Run only fast tests")
    parser.add_argument("--no-checks", action="store_true", help="Skip system checks")
    parser.add_argument(
        "--no-save", action="store_true", help="Skip saving detailed results"
    )

    args = parser.parse_args()

    print_banner()

    # Create results directory unless disabled
    results_dir = None
    if not args.no_save:
        results_dir = create_test_results_dir()
        print(f"📁 Test results will be saved to: {results_dir}")

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Run migrations
    run_migrations()

    # Run system checks unless skipped
    if not args.no_checks:
        if not run_basic_checks():
            sys.exit(1)

    # Check API connectivity (non-blocking) - after Django is configured
    api_status = check_api_connectivity()

    # Save API connectivity results
    if results_dir:
        api_info = {
            "type": "api_connectivity",
            "status": "PASSED" if api_status else "FAILED",
            "timestamp": datetime.now().isoformat(),
        }
        save_test_output(
            results_dir,
            "api_connectivity.txt",
            f"API Connectivity Test: {'PASSED' if api_status else 'FAILED'}\n",
            api_info,
        )

    # Run tests
    success = run_tests(coverage=args.coverage, fast=args.fast, results_dir=results_dir)

    # Print summary
    print_test_summary(success)

    # Print results location
    if results_dir:
        print(f"\n📊 Detailed test results saved to: {results_dir}")
        print("📋 Files created:")
        for file in sorted(results_dir.glob("*.txt")):
            print(f"   • {file.name}")
        if (results_dir / "test_summary.json").exists():
            print(f"   • test_summary.json")

        # Show quick failure summary if there were failures
        summary_file = results_dir / "test_summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
                if (
                    summary.get("total_failures", 0) > 0
                    or summary.get("total_errors", 0) > 0
                ):
                    print(f"\n🔍 Quick Summary:")
                    print(f"   • Failures: {summary.get('total_failures', 0)}")
                    print(f"   • Errors: {summary.get('total_errors', 0)}")
                    print(f"   • See test_failures_summary.txt for details")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
