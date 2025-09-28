#!/usr/bin/env python3
"""Test runner script for B-Tree implementation."""

import sys
import os
import subprocess
from pathlib import Path


def run_tests():
    """Run the comprehensive B-Tree test suite."""

    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # Test commands to run (override coverage options from pyproject.toml)
    test_commands = [
        # Quick tests (fast)
        [
            "python", "-m", "pytest",
            "tests/test_key_value_pair.py",
            "tests/test_btree_node.py",
            "tests/test_btree_index.py",
            "-v", "--tb=short", "--override-ini=addopts="
        ],

        # Performance tests (marked as slow)
        [
            "python", "-m", "pytest",
            "tests/test_btree_performance.py",
            "-v", "-m", "not slow", "--tb=short", "--override-ini=addopts="
        ],
    ]

    print("🌲 Running B-Tree Comprehensive Test Suite")
    print("=" * 50)

    all_passed = True

    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📋 Running test group {i}/{len(test_commands)}")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 30)

        try:
            result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
            print(f"✅ Test group {i} PASSED")
        except subprocess.CalledProcessError as e:
            print(f"❌ Test group {i} FAILED with exit code {e.returncode}")
            all_passed = False
        except FileNotFoundError:
            print(f"❌ Test group {i} FAILED - pytest not found")
            print("Please install pytest: pip install pytest")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Your B-Tree implementation is rock solid!")
        print("\nYour implementation successfully handles:")
        print("  ✓ Basic operations (insert, search, delete)")
        print("  ✓ Node splitting and merging")
        print("  ✓ Tree rebalancing")
        print("  ✓ Edge cases and error conditions")
        print("  ✓ Performance requirements")
        print("  ✓ Memory efficiency")
        print("  ✓ Type safety and immutability")
    else:
        print("❌ SOME TESTS FAILED - Please check the output above")
        return 1

    return 0


def run_slow_tests():
    """Run the slow/stress tests separately."""
    print("\n🐌 Running slow/stress tests (this may take a while)...")
    cmd = [
        "python", "-m", "pytest",
        "tests/test_btree_performance.py",
        "-v", "-m", "slow", "--tb=short", "-s", "--override-ini=addopts="
    ]

    try:
        subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print("✅ Slow tests PASSED")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Slow tests FAILED with exit code {e.returncode}")
        return 1


def main():
    """Main test runner."""
    if len(sys.argv) > 1 and sys.argv[1] == "--slow":
        return run_slow_tests()
    elif len(sys.argv) > 1 and sys.argv[1] == "--all":
        result1 = run_tests()
        result2 = run_slow_tests()
        return result1 or result2
    else:
        print("Usage:")
        print("  python run_tests.py          # Run standard tests")
        print("  python run_tests.py --slow   # Run slow/stress tests only")
        print("  python run_tests.py --all    # Run all tests")
        return run_tests()


if __name__ == "__main__":
    sys.exit(main())