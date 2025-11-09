#!/usr/bin/env python3
"""
Basic error handling tests (no GUI dependencies).

Tests core error handling logic without requiring PyQt6.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_file_validation():
    """Test NURBS data validation logic."""
    print("\n=== Testing File Validation ===")

    from app.export.rhino_formats import validate_nurbs_data

    # Test empty data
    is_valid, error = validate_nurbs_data({})
    assert not is_valid, "Should reject empty data"
    assert error == "NURBS data is empty"
    print(f"✓ Empty data rejected: {error}")

    # Test missing fields
    incomplete_data = {'degree_u': 3}
    is_valid, error = validate_nurbs_data(incomplete_data)
    assert not is_valid, "Should reject incomplete data"
    assert "Missing required field" in error
    print(f"✓ Missing field detected: {error}")

    # Test invalid degrees
    bad_degree_data = {
        'degree_u': 0,  # Invalid
        'degree_v': 3,
        'count_u': 4,
        'count_v': 4,
        'control_points': [[0, 0, 0]] * 16,
        'weights': [1.0] * 16,
        'knots_u': [0] * 8,
        'knots_v': [0] * 8
    }
    is_valid, error = validate_nurbs_data(bad_degree_data)
    assert not is_valid, "Should reject invalid degrees"
    assert "Invalid degrees" in error
    print(f"✓ Invalid degree detected: {error}")

    # Test dimension mismatch
    mismatch_data = {
        'degree_u': 3,
        'degree_v': 3,
        'count_u': 4,
        'count_v': 4,
        'control_points': [[0, 0, 0]] * 10,  # Should be 16
        'weights': [1.0] * 10,
        'knots_u': [0, 0, 0, 0, 1, 1, 1, 1],
        'knots_v': [0, 0, 0, 0, 1, 1, 1, 1]
    }
    is_valid, error = validate_nurbs_data(mismatch_data)
    assert not is_valid, "Should reject dimension mismatch"
    assert "Control point count mismatch" in error
    print(f"✓ Dimension mismatch detected: {error}")

    # Test valid data
    valid_data = {
        'degree_u': 3,
        'degree_v': 3,
        'count_u': 4,
        'count_v': 4,
        'control_points': [[0, 0, 0]] * 16,
        'weights': [1.0] * 16,
        'knots_u': [0, 0, 0, 0, 1, 1, 1, 1],
        'knots_v': [0, 0, 0, 0, 1, 1, 1, 1]
    }
    is_valid, error = validate_nurbs_data(valid_data)
    assert is_valid, f"Valid data should pass: {error}"
    assert error is None
    print("✓ Valid NURBS data accepted")


def test_file_io():
    """Test file I/O error handling."""
    print("\n=== Testing File I/O ===")

    from app.export.rhino_formats import write_json_export, read_json_import

    # Test write to invalid directory
    success, error = write_json_export({'test': 'data'}, '/invalid/path/file.json')
    assert not success, "Should fail for invalid path"
    assert error is not None
    print(f"✓ Invalid path write handled: {error}")

    # Test read non-existent file
    data, error = read_json_import('/nonexistent/file.json')
    assert data is None, "Should return None"
    assert "File not found" in error
    print(f"✓ Non-existent file handled: {error}")

    # Test write and read valid file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        test_data = {'test': 'value', 'number': 42}
        success, error = write_json_export(test_data, temp_path)
        assert success, f"Write should succeed: {error}"
        assert error is None
        print("✓ Write to valid path succeeded")

        read_data, error = read_json_import(temp_path)
        assert read_data is not None, f"Read should succeed: {error}"
        assert read_data == test_data
        print("✓ Read from valid path succeeded")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_logging_setup():
    """Test logging configuration."""
    print("\n=== Testing Logging Setup ===")

    import logging
    from app.utils.error_handling import setup_logging, get_logger

    # Setup logging
    setup_logging(level=logging.INFO)

    # Get logger
    logger = get_logger('test_module')
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    print("✓ Logger created successfully")

    # Test logging messages (should not raise)
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    print("✓ Logging messages work")


def test_knot_vector_validation():
    """Test knot vector validation."""
    print("\n=== Testing Knot Vector Validation ===")

    from app.export.rhino_formats import validate_nurbs_data

    # Test non-decreasing knot vector (invalid)
    invalid_knots = {
        'degree_u': 3,
        'degree_v': 3,
        'count_u': 4,
        'count_v': 4,
        'control_points': [[0, 0, 0]] * 16,
        'weights': [1.0] * 16,
        'knots_u': [1, 0, 0, 0, 0, 1, 1, 1],  # Not non-decreasing!
        'knots_v': [0, 0, 0, 0, 1, 1, 1, 1]
    }
    is_valid, error = validate_nurbs_data(invalid_knots)
    assert not is_valid, "Should reject non-monotonic knot vector"
    assert "not non-decreasing" in error
    print(f"✓ Non-monotonic knot vector detected: {error}")


def run_all_tests():
    """Run all basic error handling tests."""
    print("=" * 60)
    print("Basic Error Handling Test Suite")
    print("=" * 60)

    try:
        test_logging_setup()
        test_file_validation()
        test_knot_vector_validation()
        test_file_io()

        print("\n" + "=" * 60)
        print("✓ All basic error handling tests passed!")
        print("=" * 60)

        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
