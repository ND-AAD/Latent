#!/usr/bin/env python3
"""Test constraint validation bindings for cpp_core module."""

import sys

# Import the C++ module
try:
    import cpp_core
except ImportError as e:
    print(f"❌ Failed to import cpp_core: {e}")
    print("Make sure the module is built and in PYTHONPATH")
    sys.exit(1)


def test_constraint_level():
    """Test ConstraintLevel enum binding."""
    print("Test: ConstraintLevel enum...")
    
    # Check that enum values are accessible
    assert hasattr(cpp_core, 'ConstraintLevel')
    assert hasattr(cpp_core.ConstraintLevel, 'ERROR')
    assert hasattr(cpp_core.ConstraintLevel, 'WARNING')
    assert hasattr(cpp_core.ConstraintLevel, 'FEATURE')
    
    # Check that values are distinct
    assert cpp_core.ConstraintLevel.ERROR != cpp_core.ConstraintLevel.WARNING
    assert cpp_core.ConstraintLevel.WARNING != cpp_core.ConstraintLevel.FEATURE
    
    print("  ✅ ConstraintLevel enum binding working")


def test_constraint_violation():
    """Test ConstraintViolation struct binding."""
    print("\nTest: ConstraintViolation...")
    
    # Create a violation
    violation = cpp_core.ConstraintViolation()
    
    # Check that it has the expected readonly fields
    assert hasattr(violation, 'level')
    assert hasattr(violation, 'description')
    assert hasattr(violation, 'face_id')
    assert hasattr(violation, 'severity')
    assert hasattr(violation, 'suggestion')
    
    # Check repr
    repr_str = repr(violation)
    assert "ConstraintViolation" in repr_str
    
    print("  ✅ ConstraintViolation binding working")


def test_constraint_report():
    """Test ConstraintReport class binding."""
    print("\nTest: ConstraintReport...")
    
    # Create a report
    report = cpp_core.ConstraintReport()
    
    # Initially should have no violations
    assert len(report.violations) == 0
    assert not report.has_errors()
    assert not report.has_warnings()
    assert report.error_count() == 0
    assert report.warning_count() == 0
    
    print("  ✅ Empty report correct")
    
    # Add an error
    report.add_error("Test error", face_id=5, severity=0.8)
    assert report.has_errors()
    assert report.error_count() == 1
    assert len(report.violations) == 1
    assert report.violations[0].level == cpp_core.ConstraintLevel.ERROR
    assert report.violations[0].face_id == 5
    assert abs(report.violations[0].severity - 0.8) < 0.001
    
    print("  ✅ add_error() working")
    
    # Add a warning
    report.add_warning("Test warning", face_id=3, severity=0.5)
    assert report.has_warnings()
    assert report.warning_count() == 1
    assert report.error_count() == 1
    assert len(report.violations) == 2
    
    print("  ✅ add_warning() working")
    
    # Add a feature
    report.add_feature("Test feature", face_id=1)
    assert len(report.violations) == 3
    assert report.violations[2].level == cpp_core.ConstraintLevel.FEATURE
    
    print("  ✅ add_feature() working")
    print(f"  ✅ Report: {report.error_count()} errors, {report.warning_count()} warnings")


def test_constraint_validator():
    """Test ConstraintValidator class binding."""
    print("\nTest: ConstraintValidator...")
    
    # Create a simple quad for testing
    cage = cpp_core.SubDControlCage()
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0.1),  # Slight tilt
        cpp_core.Point3D(0, 1, 0)
    ]
    cage.faces = [[0, 1, 2, 3]]
    
    # Create evaluator
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)
    
    # Create validator
    validator = cpp_core.ConstraintValidator(evaluator)
    assert validator is not None
    
    print("  ✅ ConstraintValidator created")
    
    # Validate region
    face_indices = [0]
    demolding_direction = cpp_core.Point3D(0, 0, 1)  # Upward
    
    report = validator.validate_region(face_indices, demolding_direction)
    
    # Check that we got a report back
    assert isinstance(report, cpp_core.ConstraintReport)
    print(f"  ✅ Validation report: {report.error_count()} errors, "
          f"{report.warning_count()} warnings")
    
    # Print violations if any
    for i, violation in enumerate(report.violations):
        level_str = str(violation.level).split('.')[-1]  # Get enum name
        print(f"    Violation {i+1}: {level_str} - {violation.description}")
    
    print("  ✅ validate_region() working")


def test_full_workflow():
    """Test complete constraint validation workflow."""
    print("\nTest: Full constraint validation workflow...")
    
    # Create a cube
    cage = cpp_core.SubDControlCage()
    cage.vertices = [
        cpp_core.Point3D(0, 0, 0),
        cpp_core.Point3D(1, 0, 0),
        cpp_core.Point3D(1, 1, 0),
        cpp_core.Point3D(0, 1, 0),
        cpp_core.Point3D(0, 0, 1),
        cpp_core.Point3D(1, 0, 1),
        cpp_core.Point3D(1, 1, 1),
        cpp_core.Point3D(0, 1, 1)
    ]
    cage.faces = [
        [0, 1, 2, 3],  # bottom
        [4, 5, 6, 7],  # top
        [0, 1, 5, 4],  # front
        [2, 3, 7, 6],  # back
        [0, 3, 7, 4],  # left
        [1, 2, 6, 5]   # right
    ]
    
    # Initialize evaluator
    evaluator = cpp_core.SubDEvaluator()
    evaluator.initialize(cage)
    
    # Create validator
    validator = cpp_core.ConstraintValidator(evaluator)
    
    # Test different demolding directions
    directions = [
        ("Up (+Z)", cpp_core.Point3D(0, 0, 1)),
        ("Down (-Z)", cpp_core.Point3D(0, 0, -1)),
        ("Right (+X)", cpp_core.Point3D(1, 0, 0)),
    ]
    
    for name, direction in directions:
        print(f"\n  Testing {name} demolding direction...")
        
        # Validate top and bottom faces
        face_indices = [0, 1]  # bottom and top
        report = validator.validate_region(face_indices, direction, min_wall_thickness=3.0)
        
        print(f"    Errors: {report.error_count()}, Warnings: {report.warning_count()}")
        
        # Show first few violations
        for violation in report.violations[:3]:
            level_str = str(violation.level).split('.')[-1]
            print(f"      {level_str}: {violation.description[:60]}")
    
    print("\n  ✅ Full workflow test complete")


def main():
    """Run all constraint binding tests."""
    print("=" * 60)
    print("Testing Constraint Validation Python Bindings")
    print("=" * 60)
    
    try:
        test_constraint_level()
        test_constraint_violation()
        test_constraint_report()
        test_constraint_validator()
        test_full_workflow()
        
        print("\n" + "=" * 60)
        print("✅ ALL CONSTRAINT TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
