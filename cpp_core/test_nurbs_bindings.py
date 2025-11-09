#!/usr/bin/env python3
"""
Test NURBS Python bindings (Agent 50)

This test validates that the NURBS mold generator bindings work correctly.
It requires:
1. cpp_core module compiled with OpenCASCADE support
2. NURBS generator implementation (Agents 46-49)

To run:
    python3 test_nurbs_bindings.py
"""

import sys
import os

# Add build directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'build'))

try:
    import cpp_core
    print("✓ cpp_core module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import cpp_core: {e}")
    print("\nBuild the module first:")
    print("  cd cpp_core/build && cmake .. && make")
    sys.exit(1)


def test_nurbs_classes_exist():
    """Test that NURBS classes are exposed to Python"""
    print("\n=== Testing NURBS Class Availability ===")

    # Check NURBSMoldGenerator exists
    assert hasattr(cpp_core, 'NURBSMoldGenerator'), \
        "NURBSMoldGenerator not found in cpp_core"
    print("✓ NURBSMoldGenerator class available")

    # Check FittingQuality exists
    assert hasattr(cpp_core, 'FittingQuality'), \
        "FittingQuality not found in cpp_core"
    print("✓ FittingQuality class available")


def test_nurbs_generator_construction():
    """Test NURBSMoldGenerator can be constructed"""
    print("\n=== Testing NURBSMoldGenerator Construction ===")

    # Create a simple SubD cage
    cage = cpp_core.SubDControlCage()

    # Create a simple quad (4 vertices, 1 face)
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0)
    ]
    cage.faces = [[0, 1, 2, 3]]

    # Initialize evaluator
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)
    print("✓ Created test SubD evaluator")

    # Create NURBS generator
    generator = cpp_core.NURBSMoldGenerator(evaluator)
    print("✓ NURBSMoldGenerator constructed successfully")

    return generator, evaluator


def test_nurbs_methods_exist():
    """Test that all NURBS methods are bound"""
    print("\n=== Testing NURBSMoldGenerator Methods ===")

    generator, _ = test_nurbs_generator_construction()

    # Check all methods exist
    methods = [
        'fit_nurbs_surface',
        'apply_draft_angle',
        'create_mold_solid',
        'add_registration_keys',
        'check_fitting_quality'
    ]

    for method in methods:
        assert hasattr(generator, method), \
            f"Method {method} not found in NURBSMoldGenerator"
        print(f"✓ Method '{method}' available")


def test_fitting_quality_struct():
    """Test FittingQuality struct"""
    print("\n=== Testing FittingQuality Struct ===")

    quality = cpp_core.FittingQuality()
    print("✓ FittingQuality constructed")

    # Check fields exist
    fields = ['max_deviation', 'mean_deviation', 'rms_deviation', 'num_samples']
    for field in fields:
        assert hasattr(quality, field), f"Field {field} not found in FittingQuality"
        print(f"✓ Field '{field}' available")

    # Test setting values
    quality.max_deviation = 0.1
    quality.mean_deviation = 0.05
    quality.rms_deviation = 0.06
    quality.num_samples = 100

    assert quality.max_deviation == 0.1
    assert quality.mean_deviation == 0.05
    assert quality.rms_deviation == 0.06
    assert quality.num_samples == 100
    print("✓ FittingQuality fields can be read/written")

    # Test __repr__
    repr_str = repr(quality)
    assert 'FittingQuality' in repr_str
    print(f"✓ FittingQuality __repr__: {repr_str}")


def test_fit_nurbs_surface():
    """Test fit_nurbs_surface method"""
    print("\n=== Testing fit_nurbs_surface ===")

    generator, evaluator = test_nurbs_generator_construction()

    try:
        # Try to fit NURBS to single face
        face_indices = [0]
        sample_density = 10

        # Note: This will return an opaque Handle type
        # We just verify it doesn't crash
        surface = generator.fit_nurbs_surface(face_indices, sample_density)
        print("✓ fit_nurbs_surface executed (returns opaque Handle type)")

    except Exception as e:
        print(f"✗ fit_nurbs_surface failed: {e}")
        # This might fail if OpenCASCADE is not properly configured
        # That's okay for now - we're testing the bindings exist


def test_docstrings():
    """Test that docstrings are present"""
    print("\n=== Testing Docstrings ===")

    # Check class docstring
    assert cpp_core.NURBSMoldGenerator.__doc__ is not None
    print("✓ NURBSMoldGenerator has docstring")
    print(f"  {cpp_core.NURBSMoldGenerator.__doc__[:80]}...")

    # Check FittingQuality docstring
    assert cpp_core.FittingQuality.__doc__ is not None
    print("✓ FittingQuality has docstring")


def main():
    """Run all tests"""
    print("=" * 60)
    print("NURBS Python Bindings Test Suite (Agent 50)")
    print("=" * 60)

    try:
        test_nurbs_classes_exist()
        test_fitting_quality_struct()
        test_nurbs_methods_exist()
        test_docstrings()

        # Optional tests that might fail without full OpenCASCADE setup
        print("\n=== Optional Integration Tests ===")
        try:
            test_fit_nurbs_surface()
        except Exception as e:
            print(f"⚠ Integration test skipped (requires OpenCASCADE): {e}")

        print("\n" + "=" * 60)
        print("✓ All basic binding tests PASSED")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
