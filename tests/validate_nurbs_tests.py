#!/usr/bin/env python3
"""
Validation script for test_nurbs_generation.py

Checks that the test file is properly structured and can be imported.
"""

import sys
import os
from pathlib import Path

# Add cpp_core to path
cpp_core_path = Path(__file__).parent.parent / "cpp_core" / "build"
if cpp_core_path.exists():
    sys.path.insert(0, str(cpp_core_path))

def main():
    print("=" * 70)
    print("NURBS Generation Tests Validation")
    print("=" * 70)
    print()

    # Check if cpp_core is available
    try:
        import cpp_core
        print("✅ cpp_core module imported successfully")
        print(f"   Version: {getattr(cpp_core, '__version__', 'unknown')}")
    except ImportError as e:
        print(f"⚠️  cpp_core module not available: {e}")
        print("   This is expected if C++ module hasn't been built yet")
        return

    # Check if NURBSMoldGenerator is available
    if hasattr(cpp_core, 'NURBSMoldGenerator'):
        print("✅ NURBSMoldGenerator class is available")

        # Try to import the test module
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            import test_nurbs_generation
            print("✅ test_nurbs_generation module imported successfully")

            # List test methods
            test_class = test_nurbs_generation.TestNURBSGeneration
            test_methods = [m for m in dir(test_class) if m.startswith('test_')]
            print(f"✅ Found {len(test_methods)} test methods:")
            for method in test_methods:
                print(f"   - {method}")

            print()
            print("=" * 70)
            print("READY TO RUN TESTS")
            print("=" * 70)
            print("Run with: python3 -m pytest tests/test_nurbs_generation.py -v")
            print("=" * 70)

        except Exception as e:
            print(f"❌ Error importing test module: {e}")
            import traceback
            traceback.print_exc()

    else:
        print("⚠️  NURBSMoldGenerator not yet available in cpp_core")
        print("   This is expected - waiting for Agents 46-50 to complete")
        print()
        print("   The test file has been created and is ready.")
        print("   Tests will be skipped until NURBSMoldGenerator is implemented.")
        print()

        # Verify test file structure
        test_file = Path(__file__).parent / "test_nurbs_generation.py"
        if test_file.exists():
            print(f"✅ Test file created: {test_file}")
            print(f"   Size: {test_file.stat().st_size} bytes")

            # Count test methods
            with open(test_file) as f:
                content = f.read()
                test_count = content.count('def test_')
                print(f"   Test methods: {test_count}")

        print()
        print("=" * 70)
        print("TESTS READY - WAITING FOR IMPLEMENTATION")
        print("=" * 70)

if __name__ == "__main__":
    main()
