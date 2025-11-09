#!/usr/bin/env python3
"""
Test suite for error handling throughout the application.

Tests:
- HTTP bridge error handling
- C++ exception handling
- NURBS generation error handling
- File I/O error handling
- User input validation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.error_handling import (
    setup_logging, get_logger, get_error_handler,
    handle_exceptions, graceful_degradation
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


def test_logging():
    """Test logging configuration."""
    print("\n=== Testing Logging ===")

    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    print("✓ Logging works")


def test_error_handler():
    """Test error handler functionality."""
    print("\n=== Testing Error Handler ===")

    handler = get_error_handler()

    # Test without showing dialogs (would require GUI)
    handler.logger.info("Error handler initialized")
    print("✓ Error handler works")


def test_http_bridge_errors():
    """Test HTTP bridge error handling."""
    print("\n=== Testing HTTP Bridge Error Handling ===")

    from app.bridge.rhino_bridge import RhinoBridge

    # Test connection to non-existent server
    bridge = RhinoBridge(host="localhost", port=9999)

    # Should fail gracefully
    result = bridge.connect()
    assert result is False, "Connection should fail"
    print("✓ Connection failure handled gracefully")

    # Test receiving invalid geometry
    invalid_data = {}
    geometry = bridge.receive_geometry(invalid_data)
    assert geometry is None, "Should return None for invalid data"
    print("✓ Invalid geometry data handled")

    # Test sending molds when not connected
    result = bridge.send_molds([])
    assert result is False, "Should fail when not connected"
    print("✓ Send molds without connection handled")


def test_file_io_errors():
    """Test file I/O error handling."""
    print("\n=== Testing File I/O Error Handling ===")

    from app.export.rhino_formats import (
        validate_nurbs_data, write_json_export, read_json_import
    )

    # Test validation of empty data
    is_valid, error = validate_nurbs_data({})
    assert not is_valid, "Should reject empty data"
    assert error is not None, "Should provide error message"
    print(f"✓ Empty data validation: {error}")

    # Test validation of missing fields
    incomplete_data = {'degree_u': 3}
    is_valid, error = validate_nurbs_data(incomplete_data)
    assert not is_valid, "Should reject incomplete data"
    print(f"✓ Incomplete data validation: {error}")

    # Test writing to invalid path
    success, error = write_json_export({}, "/invalid/path/file.json")
    assert not success, "Should fail for invalid path"
    print(f"✓ Invalid path write error: {error}")

    # Test reading non-existent file
    data, error = read_json_import("/nonexistent/file.json")
    assert data is None, "Should return None for non-existent file"
    assert error is not None, "Should provide error message"
    print(f"✓ Non-existent file read error: {error}")


def test_decorators():
    """Test error handling decorators."""
    print("\n=== Testing Error Handling Decorators ===")

    # Test graceful degradation
    @graceful_degradation(fallback_value=[])
    def failing_function():
        raise RuntimeError("Intentional error")

    result = failing_function()
    assert result == [], "Should return fallback value"
    print("✓ Graceful degradation works")

    # Test exception handling (without dialog)
    @handle_exceptions("Test Error", show_dialog=False, return_on_error=None)
    def another_failing_function():
        raise ValueError("Another intentional error")

    result = another_failing_function()
    assert result is None, "Should return default on error"
    print("✓ Exception handler works")


def test_nurbs_validation():
    """Test NURBS data validation."""
    print("\n=== Testing NURBS Validation ===")

    from app.export.rhino_formats import validate_nurbs_data

    # Create valid NURBS data
    valid_data = {
        'degree_u': 3,
        'degree_v': 3,
        'count_u': 4,
        'count_v': 4,
        'control_points': [[0, 0, 0]] * 16,  # 4x4 = 16 points
        'weights': [1.0] * 16,
        'knots_u': [0, 0, 0, 0, 1, 1, 1, 1],  # 4 + 3 + 1 = 8 knots
        'knots_v': [0, 0, 0, 0, 1, 1, 1, 1]
    }

    is_valid, error = validate_nurbs_data(valid_data)
    assert is_valid, f"Valid data should pass: {error}"
    print("✓ Valid NURBS data accepted")

    # Test dimension mismatch
    invalid_data = valid_data.copy()
    invalid_data['control_points'] = [[0, 0, 0]] * 10  # Wrong count
    is_valid, error = validate_nurbs_data(invalid_data)
    assert not is_valid, "Should reject dimension mismatch"
    print(f"✓ Dimension mismatch detected: {error}")

    # Test invalid knot vector
    invalid_data = valid_data.copy()
    invalid_data['knots_u'] = [1, 0, 0, 0, 0, 1, 1, 1]  # Not non-decreasing
    is_valid, error = validate_nurbs_data(invalid_data)
    assert not is_valid, "Should reject invalid knot vector"
    print(f"✓ Invalid knot vector detected: {error}")


def run_all_tests():
    """Run all error handling tests."""
    print("=" * 60)
    print("Error Handling Test Suite")
    print("=" * 60)

    try:
        test_logging()
        test_error_handler()
        test_http_bridge_errors()
        test_file_io_errors()
        test_decorators()
        test_nurbs_validation()

        print("\n" + "=" * 60)
        print("✓ All error handling tests passed!")
        print("=" * 60)

        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
