#!/usr/bin/env python3
"""
Validation script for export and round-trip tests.

Verifies test structure and runs basic validation without pytest.

Author: Agent 57 (Day 8 Morning)
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
    print("Export and Round-Trip Tests Validation")
    print("=" * 70)
    print()

    # Check if cpp_core is available
    try:
        import cpp_core
        print("✅ cpp_core module imported successfully")
        print(f"   Version: {getattr(cpp_core, '__version__', 'unknown')}")
    except ImportError as e:
        print(f"⚠️  cpp_core module not available: {e}")
        print("   Build cpp_core first: cd cpp_core/build && cmake .. && make")
        return

    # Check if NURBSMoldGenerator is available
    if not hasattr(cpp_core, 'NURBSMoldGenerator'):
        print("⚠️  NURBSMoldGenerator not yet available in cpp_core")
        print("   Tests will be skipped until implementation is complete")
        return

    print("✅ NURBSMoldGenerator class is available")

    # Check export module
    try:
        from app.export.nurbs_serializer import NURBSSerializer, RhinoNURBSSurface
        from app.export.rhino_formats import validate_nurbs_data, write_json_export
        print("✅ Export modules imported successfully")
    except ImportError as e:
        print(f"❌ Error importing export modules: {e}")
        return

    # Verify test files exist
    test_files = ['test_export.py', 'test_roundtrip.py']
    for test_file in test_files:
        path = Path(__file__).parent / test_file
        if path.exists():
            print(f"✅ {test_file} exists ({path.stat().st_size} bytes)")

            # Count test methods
            with open(path) as f:
                content = f.read()
                test_count = content.count('def test_')
                print(f"   Found {test_count} test methods")
        else:
            print(f"❌ {test_file} not found")

    print()
    print("=" * 70)
    print("Running Basic Validation Tests")
    print("=" * 70)
    print()

    # Run basic validation
    success_count = 0
    total_count = 0

    # Test 1: Create simple NURBS and serialize
    total_count += 1
    try:
        print("Test 1: Basic NURBS serialization...")
        cage = cpp_core.SubDControlCage()
        cage.vertices = [
            cpp_core.Point3D(0, 0, 0),
            cpp_core.Point3D(1, 0, 0),
            cpp_core.Point3D(1, 1, 0),
            cpp_core.Point3D(0, 1, 0)
        ]
        cage.faces = [[0, 1, 2, 3]]

        evaluator = cpp_core.SubDEvaluator()
        evaluator.initialize(cage)

        generator = cpp_core.NURBSMoldGenerator(evaluator)
        nurbs = generator.fit_nurbs_surface([0], sample_density=20)

        serializer = NURBSSerializer()
        rhino_surf = serializer.serialize_surface(nurbs, name="test")

        assert rhino_surf.degree_u > 0
        assert rhino_surf.degree_v > 0
        assert len(rhino_surf.control_points) > 0
        print("   ✅ PASS: Basic serialization works")
        success_count += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Test 2: JSON round-trip
    total_count += 1
    try:
        print("Test 2: JSON round-trip...")
        import json
        data = rhino_surf.to_dict()
        json_str = json.dumps(data)
        recovered = json.loads(json_str)

        assert recovered['degree_u'] == data['degree_u']
        assert recovered['degree_v'] == data['degree_v']
        assert len(recovered['control_points']) == len(data['control_points'])
        print("   ✅ PASS: JSON round-trip works")
        success_count += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Test 3: Validation
    total_count += 1
    try:
        print("Test 3: NURBS data validation...")
        assert validate_nurbs_data(data)
        print("   ✅ PASS: Validation works")
        success_count += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Test 4: Mold set export
    total_count += 1
    try:
        print("Test 4: Mold set export...")
        molds = [
            (generator.fit_nurbs_surface([0], 20), 1),
            (generator.fit_nurbs_surface([0], 20), 2),
        ]

        export_data = serializer.serialize_mold_set(
            molds,
            metadata={'draft_angle': 2.0}
        )

        assert export_data['type'] == 'ceramic_mold_set'
        assert len(export_data['molds']) == 2
        print("   ✅ PASS: Mold set export works")
        success_count += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Test 5: Knot vector validation
    total_count += 1
    try:
        print("Test 5: Knot vector validation...")
        # Check knots are non-decreasing
        for i in range(len(rhino_surf.knots_u) - 1):
            assert rhino_surf.knots_u[i] <= rhino_surf.knots_u[i+1]
        for i in range(len(rhino_surf.knots_v) - 1):
            assert rhino_surf.knots_v[i] <= rhino_surf.knots_v[i+1]
        print("   ✅ PASS: Knot vectors valid")
        success_count += 1
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    print()
    print("=" * 70)
    print(f"Validation Results: {success_count}/{total_count} tests passed")
    print("=" * 70)
    print()

    if success_count == total_count:
        print("✅ ALL VALIDATION TESTS PASSED")
        print()
        print("Export test suite is ready!")
        print()
        print("To run full test suite (requires pytest):")
        print("  python3 -m pytest tests/test_export.py -v")
        print("  python3 -m pytest tests/test_roundtrip.py -v")
        return 0
    else:
        print("⚠️  Some validation tests failed")
        print("   Check the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
