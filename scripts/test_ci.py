#!/usr/bin/env python3
"""
CI test script for ManifoldBot.

This script runs basic tests that don't require API keys,
and optionally runs real API tests if keys are available.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {cmd}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        return True
    else:
        print(f"❌ {description} - FAILED")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False


def main():
    """Run CI tests."""
    print("🚀 Starting ManifoldBot CI Tests")
    print("=" * 50)

    # Check if we're in the right directory
    if not Path("manifoldbot").exists():
        print("❌ Error: Please run this script from the project root")
        sys.exit(1)

    tests_passed = 0
    total_tests = 0

    # Test 1: Package installation
    total_tests += 1
    if run_command(
        "python -c 'from manifoldbot import ManifoldReader, ManifoldWriter; print(\"Package imports work\")'",
        "Package Installation",
    ):
        tests_passed += 1

    # Test 2: Basic initialization
    total_tests += 1
    if run_command(
        'python -c \'from manifoldbot import ManifoldReader, ManifoldWriter; r=ManifoldReader(); w=ManifoldWriter("test"); print("Initialization works")\'',
        "Basic Initialization",
    ):
        tests_passed += 1

    # Test 3: Unit tests (no API calls)
    total_tests += 1
    if run_command("pytest tests/manifold/test_reader.py::TestManifoldReader -v --tb=short", "Unit Tests (Reader)"):
        tests_passed += 1

    # Test 4: Writer unit tests
    total_tests += 1
    if run_command("pytest tests/manifold/test_writer.py -v --tb=short", "Unit Tests (Writer)"):
        tests_passed += 1

    # Test 5: Real API tests (if keys available)
    manifold_key = os.getenv("MANIFOLD_API_KEY")
    if manifold_key:
        total_tests += 1
        if run_command("pytest tests/manifold/test_reader_real.py -v --tb=short", "Real API Tests"):
            tests_passed += 1
    else:
        print("\n⚠️  Skipping real API tests - MANIFOLD_API_KEY not set")

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
